from time import time

from pianobot import Pianobot

async def worlds(bot: Pianobot):
    world_names = {world.world for world in bot.database.worlds.get_all()}
    online_players = await bot.corkus.network.online_players()

    for server in online_players.servers:
        if server.name in world_names:
            world_names.remove(server.name)
        else:
            bot.database.worlds.add(server.name, time())

    for world in world_names:
        bot.database.worlds.remove(world)
