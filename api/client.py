"""Async HTTP client for the Wynncraft v3 API with bucket-aware rate limiting."""

import asyncio
import logging
from collections.abc import Mapping
from uuid import UUID

from aiohttp import ClientSession, ClientTimeout

from api.exceptions import NotFoundError, RateLimitedError, WynncraftError
from api.models import (
    Guild,
    GuildLeaderboardEntry,
    GuildLeaderboardResponse,
    GuildListResponse,
    OnlinePlayers,
    OnlinePlayersByUuid,
    Player,
    TerritoryList,
    TerritorySnapshot,
)

log = logging.getLogger(__name__)


class WynncraftClient:
    """Thin wrapper around `/v3` endpoints we actually use."""

    BASE = "https://api.wynncraft.com/v3"
    TIMEOUT = ClientTimeout(total=30)

    def __init__(self, session: ClientSession, token: str | None = None) -> None:
        """Wrap an `aiohttp.ClientSession`; a token raises the rate limit."""
        self._session = session
        self._token = token
        self._bucket_block_until: dict[str, float] = {}

    def _headers(self) -> dict[str, str]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    async def _get(self, path: str, *, retries: int = 3) -> bytes:
        url = f"{self.BASE}{path}"
        bucket = path.replace("?", "/").split("/", 2)[1]
        for attempt in range(retries + 1):
            await self._respect_bucket(bucket)
            try:
                async with self._session.get(
                    url, headers=self._headers(), timeout=self.TIMEOUT
                ) as response:
                    self._track_ratelimit(bucket, response.headers)
                    if response.status == 404:
                        raise NotFoundError(url)
                    if response.status == 429:
                        retry_after = float(
                            response.headers.get("RateLimit-Reset", "5")
                        )
                        if attempt == retries:
                            raise RateLimitedError(retry_after)
                        log.warning("%s 429; sleeping %.1fs", path, retry_after)
                        await asyncio.sleep(retry_after)
                        continue
                    if response.status >= 500:
                        if attempt == retries:
                            raise WynncraftError(f"{response.status} on {url}")
                        await asyncio.sleep(2**attempt)
                        continue
                    if response.status != 200:
                        text = await response.text()
                        raise WynncraftError(
                            f"{response.status} on {url}: {text[:200]}"
                        )
                    return await response.read()
            except TimeoutError:
                if attempt == retries:
                    raise WynncraftError(f"timeout on {url}") from None
                await asyncio.sleep(2**attempt)
        raise WynncraftError(f"exhausted retries on {url}")

    async def _respect_bucket(self, bucket: str) -> None:
        if (block_until := self._bucket_block_until.get(bucket)) is None:
            return
        if (delay := block_until - asyncio.get_event_loop().time()) > 0:
            await asyncio.sleep(delay)

    def _track_ratelimit(self, bucket: str, headers: Mapping[str, str]) -> None:
        remaining = headers.get("RateLimit-Remaining")
        reset = headers.get("RateLimit-Reset")
        if remaining is None or reset is None:
            return
        try:
            remaining_i = int(remaining)
            reset_f = float(reset)
        except ValueError:
            return
        if remaining_i <= 2:
            now = asyncio.get_event_loop().time()
            self._bucket_block_until[bucket] = now + reset_f

    async def get_guild(self, name: str) -> Guild:
        """Fetch a guild by name."""
        return Guild.model_validate_json(await self._get(f"/guild/{name}"))

    async def get_uuid_guild(self, uuid: UUID) -> Guild:
        """Fetch a guild by UUID."""
        return Guild.model_validate_json(await self._get(f"/guild/uuid/{uuid}"))

    async def get_player(self, query: str | UUID) -> Player:
        """Fetch a player's main stats by username or uuid."""
        return Player.model_validate_json(await self._get(f"/player/{query}"))

    async def get_online_players(self) -> OnlinePlayers:
        """List currently online players keyed by username."""
        return OnlinePlayers.model_validate_json(await self._get("/player"))

    async def get_online_players_by_uuid(self) -> OnlinePlayersByUuid:
        """List currently online players keyed by UUID."""
        return OnlinePlayersByUuid.model_validate_json(
            await self._get("/player?identifier=uuid")
        )

    async def get_guild_leaderboard(
        self, lb_type: str, limit: int = 100
    ) -> list[GuildLeaderboardEntry]:
        """Fetch a leaderboard (e.g. guildLevel) limited to `limit` entries."""
        raw = await self._get(f"/leaderboards/{lb_type}?resultLimit={limit}")
        return GuildLeaderboardResponse.model_validate_json(raw).root

    async def get_guild_list(self) -> dict[UUID, tuple[str, str]]:
        """All guilds on the network keyed by uuid: ``{uuid: (name, prefix)}``."""
        raw = await self._get("/guild/list/guild")
        return GuildListResponse.model_validate_json(raw).to_uuid_map()

    async def get_territories(self) -> list[TerritorySnapshot]:
        """Snapshot of every map territory with its owning guild (if any)."""
        raw = await self._get("/guild/list/territory")
        return TerritoryList.model_validate_json(raw).root
