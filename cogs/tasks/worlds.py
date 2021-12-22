from time import time

from ..bot import Pianobot

async def run(bot: Pianobot) -> None:
    world_names = {world.world for world in bot.db.worlds.get_all()}
    online_players = await bot.corkus.network.online_players()
    
    for server in online_players.servers:
        if server.name in world_names:
            world_names.remove(server.name)
        else:
            bot.db.worlds.add(server.name, time())

    for world in world_names:
        bot.db.worlds.remove(world)
