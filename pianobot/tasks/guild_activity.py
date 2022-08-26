from __future__ import annotations

from asyncio import gather
from logging import getLogger
from typing import TYPE_CHECKING

from corkus import Corkus
from corkus.errors import CorkusTimeoutError
from corkus.objects.online_players import OnlinePlayers

if TYPE_CHECKING:
    from pianobot import Pianobot


async def guild_activity(bot: Pianobot) -> None:
    guilds: dict[str, int | None] = {guild: None for guild in bot.tracked_guilds}
    try:
        players = await bot.corkus.network.online_players()
    except CorkusTimeoutError:
        getLogger('tasks.guild_activity').warning('Error when fetching list of online players')
        return

    for result in await gather(*[fetch(bot.corkus, guild, players) for guild in guilds]):
        if result is not None:
            guilds.update(result)

    await bot.database.guild_activity.add(guilds)


async def fetch(corkus: Corkus, name: str, players: OnlinePlayers) -> dict[str, int] | None:
    try:
        guild = await corkus.guild.get(name)
        return {guild.name: sum(players.is_player_online(m.username) for m in guild.members)}
    except CorkusTimeoutError:
        getLogger('tasks.guild_activity').warning('Error when fetching guild data of `%s`', name)
        return None
