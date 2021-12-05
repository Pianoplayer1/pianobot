from ..bot import Pianobot
from datetime import datetime

async def run(bot : Pianobot) -> None:
    db_members = dict(bot.query("SELECT uuid, name FROM members"))
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
        eden = await response.json()
        for member in eden['members']:
            if member['uuid'] not in db_members:
                epoch = (datetime.strptime(member['joined'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
                bot.query("INSERT INTO members(uuid, joined) VALUES (%s, %s)", (member['uuid'], epoch))
            bot.query("UPDATE members SET name=%s, rank=%s, xp=%s WHERE uuid=%s", (member['name'], member['rank'].capitalize(), member['contributed'], member['uuid']))

    db_lb = {a : {'level' : b,'xp' : c,'territories' : d,'warCount' : e,'membersCount' : f} for _,a,b,c,d,e,f,_ in bot.query("SELECT * FROM guilds")}
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=statsLeaderboard&type=guild&timeframe=alltime') as response:
        leaderboard = await response.json()
        properties = ['level', 'xp', 'territories', 'warCount', 'membersCount']
        for guild in leaderboard['data']:
            if 'warCount' not in guild:
                guild['warCount'] = 0
            try:
                if any(guild[prop] != db_lb[guild['prefix']][prop] for prop in properties):
                    bot.query("UPDATE guilds SET level=%s, xp=%s, territories=%s, warcount=%s, members=%s WHERE tag=%s", (guild['level'], guild['xp'], guild['territories'], guild['warCount'], guild['membersCount'], guild['prefix']))
            except KeyError:
                epoch = (datetime.strptime(guild['created'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
                bot.query("INSERT INTO guilds VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (guild['name'], guild['prefix'], guild['level'], guild['xp'], guild['territories'], guild['warCount'], guild['membersCount'], epoch))