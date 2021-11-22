from functions.db import query
from datetime import datetime, timedelta, tzinfo
import aiohttp, time, asyncio
guilds = {}

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
            if member['uuid'] not in db_members:
                epoch = (datetime.strptime(member['joined'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
                query("INSERT INTO members(uuid, joined) VALUES (%s, %s)", (member['uuid'], epoch))
            query("UPDATE members SET name=%s, rank=%s, xp=%s WHERE uuid=%s", (member['name'], member['rank'].capitalize(), member['contributed'], member['uuid']))

    db_lb = {a : {'level' : b,'xp' : c,'territories' : d,'warCount' : e,'membersCount' : f} for _,a,b,c,d,e,f,_ in query("SELECT * FROM guilds")}
    async with aiohttp.ClientSession() as session, session.get('https://api.wynncraft.com/public_api.php?action=statsLeaderboard&type=guild&timeframe=alltime') as response:
        leaderboard = await response.json()
        properties = ['level', 'xp', 'territories', 'warCount', 'membersCount']
        for guild in leaderboard['data']:
            if 'warCount' not in guild:
                guild['warCount'] = 0
            try:
                if any(guild[prop] != db_lb[guild['prefix']][prop] for prop in properties):
                    query("UPDATE guilds SET level=%s, xp=%s, territories=%s, warcount=%s, members=%s WHERE tag=%s", (guild['level'], guild['xp'], guild['territories'], guild['warCount'], guild['membersCount'], guild['prefix']))
            except KeyError:
                epoch = (datetime.strptime(guild['created'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
                query("INSERT INTO guilds VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (guild['name'], guild['prefix'], guild['level'], guild['xp'], guild['territories'], guild['warCount'], guild['membersCount'], epoch))

async def guild_activity():
    global guilds

    async with aiohttp.ClientSession() as session:
        serverList = await session.get('https://api.wynncraft.com/public_api.php?action=onlinePlayers')
        serverList = await serverList.json()
        guilds = {guild: None for guild in ['ShadowFall', 'Avicia', 'IceBlue Team', 'Guardian of Wynn', 'The Mage Legacy', 'Emorians', 'Paladins United', 'Lux Nova', 'HackForums', 'The Aquarium', 'The Simple Ones', 'Empire of Sindria', 'Titans Valor', 'The Dark Phoenix', 'Nethers Ascent', 'Sins of Seedia', 'WrathOfTheFallen', 'busted moments', 'Nefarious Ravens', 'Aequitas', 'Eden', 'KongoBoys', 'Nerfuria']}
        await asyncio.gather(*[fetch(serverList, session, guild) for guild in guilds])

        time = datetime.utcnow()
        if time.day == 31:
            return
        roundTo = 60 * 5                                            # Round to 5 minute steps as this function runs every 5 minutes
        seconds = (time.replace(tzinfo=None) - time.min).seconds
        rounded_time = (seconds+roundTo/2) // roundTo * roundTo
        rounded_time = str(time + timedelta(0,rounded_time-seconds,-time.microsecond))

        sql = f'INSERT INTO guildActivity(`time`, `{"`, `".join(guilds.keys())}`) VALUES (%s{", %s" * len(guilds)})'
        variables = (rounded_time, *guilds.values())

        try:
            query(sql, variables)
        except Exception:
<<<<<<< HEAD
            print('Duplicate in guild activity times, skipping.')
=======
            print('Duplicate guild activity time')
>>>>>>> 6911977a68c7b0170db3463002348b628a9d4405

async def fetch(serverList, session, guild):
    global guilds
    async with session.get(f'https://api.wynncraft.com/public_api.php?action=guildStats&command={guild}') as response:
        response = await response.json()
        count = sum( any(player['name'] in server for server in serverList.values()) for player in response['members'])

        guilds[guild] = count

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
