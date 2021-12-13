from ..bot import Pianobot
from time import time

async def run(bot : Pianobot) -> None:
    db_servers = dict(bot.query('SELECT world, time FROM worlds;'))
    online_players = await bot.corkus.network.online_players()
    
    for server in online_players.servers:
        if server.name in db_servers.keys():
            db_servers.pop(server.name)
        else:
            bot.query('INSERT INTO worlds (world, time) VALUES (%s, %s);', (server.name, time()))

    for world in db_servers:
        bot.query('DELETE FROM worlds WHERE world = %s;', world)