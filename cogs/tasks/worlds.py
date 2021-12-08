from ..bot import Pianobot
from time import time

async def run(bot : Pianobot) -> None:
    db_servers = bot.query('SELECT `world`, `time` FROM `worlds`;')
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=onlinePlayers') as response:
        response = await response.json()
        servers = [server for server in response.keys() if 'WC' in server]
        
        for server in db_servers:
            if server[0] in servers:
                servers.remove(server[0])
            else:
                bot.query('DELETE FROM `worlds` WHERE `world` = %s;', (server[0],))

        for server in servers:
            bot.query('INSERT INTO `worlds` (`world`, `time`) VALUES (%s, %s);', (server, time()))