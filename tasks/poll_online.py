"""Poll the online-player list; update last-seen, world uptime, and per-day minutes."""

from __future__ import annotations

import logging
from collections import Counter
from typing import TYPE_CHECKING

from api import WynncraftError
from database import snapshots, world_state

if TYPE_CHECKING:
    from client import Pianobot


log = logging.getLogger(__name__)


async def poll_online(bot: Pianobot) -> None:
    """Update last-seen, world uptimes, and per-player daily activity."""
    try:
        online = await bot.api.get_online_players_by_uuid()
    except WynncraftError as exc:
        log.warning("Online fetch failed: %s", exc)
        return

    if not online.players:
        log.warning("Online payload empty; skipping to avoid false deletes")
        return

    if online_uuids := set(online.players.keys()):
        await world_state.touch_players(bot.pool, online_uuids)
    servers = {srv for srv in online.players.values() if srv}
    await world_state.sync_worlds(bot.pool, servers)

    world_counts = Counter(srv for srv in online.players.values() if srv)
    if world_counts:
        await snapshots.record_online_counts(bot.pool, dict(world_counts))

    if online_uuids:
        await snapshots.increment_daily(bot.pool, list(online_uuids))
