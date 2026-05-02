"""Daily maintenance: thin long-tail snapshots + refresh the tracked-guild set."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from api import WynncraftError
from database import eden, guild_metrics, snapshots, tracked_guilds

if TYPE_CHECKING:
    from client import Pianobot


log = logging.getLogger(__name__)


async def cleanup_snapshots(bot: Pianobot) -> None:
    """Thin long-tail snapshot rows across every time-series table."""
    await guild_metrics.cleanup(bot.pool)
    await eden.cleanup_xp(bot.pool)
    await snapshots.cleanup_daily(bot.pool)
    await snapshots.cleanup_online_counts(bot.pool)


async def refresh_tracked_guilds(bot: Pianobot) -> None:
    """Pull top 100 of each guild leaderboard and update the tracked set."""
    merged: dict[UUID, tuple[str, str]] = {}
    for lb in ("guildLevel", "guildTerritories", "guildWars", "guildTotalRaids"):
        try:
            entries = await bot.api.get_guild_leaderboard(lb)
        except WynncraftError as exc:
            log.warning("Leaderboard %s fetch failed: %s", lb, exc)
            continue
        for entry in entries:
            if entry.uuid is None:
                continue
            merged[entry.uuid] = (entry.name, entry.prefix)
    if not merged:
        return
    await tracked_guilds.refresh(bot.pool, merged, keep_uuids=[bot.eden_wynn_uuid])
    log.info("Refreshed tracked guilds: %d entries", len(merged))
