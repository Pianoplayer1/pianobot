from functions.db import query
import aiohttp, time

async def worlds():
    db_servers = query("SELECT * FROM worlds")
    async with aiohttp.ClientSession() as session, session.get('https://api.wynncraft.com/public_api.php?action=onlinePlayers') as response:
        response = await response.json()
        servers = [server for server in response.keys() if 'WC' in server]
        
        for server in db_servers:
            if server[0] in servers:
                servers.remove(server[0])
            else:
                query("DELETE FROM worlds WHERE world = %s", server[0])

        for server in servers:
            query("INSERT INTO worlds VALUES (%s, %s)", (server, time.time()))