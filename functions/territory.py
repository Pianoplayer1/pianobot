from functions.db import query
import aiohttp, time

async def territory(client):
    servers = query("SELECT * FROM servers")
    db_terrs = dict(query("SELECT * FROM territories"))
    async with aiohttp.ClientSession() as session, session.get('https://api.wynncraft.com/public_api.php?action=territoryList') as response:
        terrs = await response.json()
        terrs = terrs['territories']
        tmissing = []

        for terr in list(db_terrs.keys()):
            if terrs[terr]['guild'] != 'Eden':
                tmissing.append(terr)
                if db_terrs[terr] == 'Eden':
                    ping_terr = terr
            if db_terrs[terr] != terrs[terr]['guild']:  
                query("UPDATE territories SET guild = %s WHERE name = %s", (terrs[terr]['guild'], terr))
                print(f'{terr}: {db_terrs[terr]} -> {terrs[terr]["guild"]}')

        if 'ping_terr' in locals():
            msg = f'{terrs[ping_terr]["guild"]} has taken control of {ping_terr}!```All missing territories ({len(tmissing)}):\n'
            for terr in tmissing:
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