from ..bot import Pianobot
from datetime import datetime

async def run(bot : Pianobot) -> None:
    db_leaderboard = bot.query('SELECT `tag`, `level`, `xp`, `territories`, `warcount`, `members` FROM `guilds`;')
    db_leaderboard = {a : {'level': b, 'xp': c, 'territories': d, 'warCount': e, 'membersCount': f} for a, b, c, d, e, f in db_leaderboard}
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=statsLeaderboard&type=guild&timeframe=alltime') as response:
        leaderboard = await response.json()
        properties = ['level', 'xp', 'territories', 'warCount', 'membersCount']
        for guild in leaderboard['data']:
            if 'warCount' not in guild:
                guild['warCount'] = 0
            try:
                if any(guild[prop] != db_leaderboard[guild['prefix']][prop] for prop in properties):
                    bot.query("UPDATE guilds SET level=%s, xp=%s, territories=%s, warcount=%s, members=%s WHERE tag=%s", (guild['level'], guild['xp'], guild['territories'], guild['warCount'], guild['membersCount'], guild['prefix']))
                db_leaderboard.pop(guild['prefix'])
            except KeyError:
                epoch = (datetime.strptime(guild['created'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
                bot.query("INSERT INTO guilds VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (guild['name'], guild['prefix'], guild['level'], guild['xp'], guild['territories'], guild['warCount'], guild['membersCount'], epoch))
        
        if (len(db_leaderboard)) == 0:
            return
        placeholders = ', '.join(['%s' for _ in db_leaderboard])
        bot.query(f'DELETE FROM `guilds` WHERE `tag` IN ({placeholders})', tuple(db_leaderboard.keys()))