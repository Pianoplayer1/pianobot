from functions.db import query
from datetime import datetime
import aiohttp, time

async def territory(client):
    servers = query("SELECT * FROM servers")
    db_terrs = dict(query("SELECT * FROM territories"))
    async with aiohttp.ClientSession() as session, session.get('https://api.wynncraft.com/public_api.php?action=territoryList') as response:
        terrs = await response.json()
        terrs = terrs['territories']

        for terr in list(db_terrs.keys()):
            if terrs[terr]['guild'] != 'Eden' and db_terrs[terr] == 'Eden':
                ping_terr = terr
            if db_terrs[terr] != terrs[terr]['guild']:  
                query("UPDATE territories SET guild = %s WHERE name = %s", (terrs[terr]['guild'], terr))
                print(f'{terr}: {db_terrs[terr]} -> {terrs[terr]["guild"]}')

        if 'ping_terr' in locals():
            tmissing = query("SELECT name FROM territories WHERE guild != 'Eden'")
            msg = f'{terrs[ping_terr]["guild"]} has taken control of {ping_terr}!```All missing territories ({len(tmissing)}):\n'
            for terr in tmissing:
                terr = terr[0]
                msg += f'\n- {terr} ({terrs[terr]["guild"]})'
            msg += '```'

            for server in servers:
                msgTemp = msg
                if server[3] != 0 and time.time() >= (server[4] + server[5]) and server[5] != 0:
                    msgTemp = f'<@&{server[3]}>\n' + msg
                    query("UPDATE servers SET time = %s WHERE id = %s", (time.time(), server[0]))
                try:
                    await client.get_channel(server[2]).send(msgTemp)
                except:
                    print(f'Couldn\'t send message to server {server[0]}')

async def guilds():
    db_members = dict(query("SELECT uuid, name FROM members"))
    async with aiohttp.ClientSession() as session, session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
        eden = await response.json()
        for member in eden['members']:
            if member['uuid'] in db_members:
                epoch = (datetime.strptime(member['joined'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
                query("UPDATE members SET name=%s, rank=%s, joined=%s, xp=%s WHERE uuid=%s", member['name'], member['rank'].capitalize(), epoch, member['contributed'], member['uuid'])
            else:
                epoch = (datetime.strptime(member['joined'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
                query("INSERT INTO members VALUES (%s, %s, 0, %s, %s, 0, 0, %s)", member['uuid'], member['name'], member['rank'].capitalize(), epoch, member['contributed'])

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