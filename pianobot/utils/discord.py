from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Guild

if TYPE_CHECKING:
    from pianobot.db import ServerTable


async def get_prefix(servers: ServerTable, guild: Guild | None) -> str:
    if guild is not None:
        server = await servers.get(guild.id)
        if server is not None:
            return server.prefix
    return '-'
