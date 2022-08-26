from __future__ import annotations

from logging import getLogger
from time import time
from typing import TYPE_CHECKING

from corkus.errors import CorkusTimeoutError

if TYPE_CHECKING:
    from pianobot import Pianobot


async def worlds(bot: Pianobot) -> None:
    world_names = {world.world for world in await bot.database.worlds.get_all()}
    try:
        online_players = await bot.corkus.network.online_players()
    except CorkusTimeoutError:
        getLogger('tasks.worlds').warning('Error when fetching list of online players')
        return

    for server in online_players.servers:
        if server.name in world_names:
            world_names.remove(server.name)
        else:
            await bot.database.worlds.add(server.name, time())

    for world in world_names:
        await bot.database.worlds.remove(world)
