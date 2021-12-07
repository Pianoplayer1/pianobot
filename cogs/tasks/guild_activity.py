import asyncio
from ..bot import Pianobot
from datetime import datetime, timedelta

async def run(bot : Pianobot) -> None:
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=onlinePlayers') as response:
        response = await response.json()
        players = set([player for server in response.values() if type(server) == list for player in server])
        guilds = {guild: None for guild in ['Achte Shadow', 'Aequitas', 'Atlas Inc', 'Avicia', 'Blacklisted', 'Breadskate', 'Crystal Iris', 'Cyphrus Code', 'Eden', 'Emorians', 'Empire of Sindria', 'FlameKnights', 'Forever Twilight', 'ForsakenLaws', 'Fuzzy Spiders', 'Gabameno', 'Germany', 'Gopniks', 'Guardian of Wynn', 'HackForums', 'IceBlue Team', 'Idiot Co', 'Jasmine Dragon', 'Jeus', 'Kingdom Foxes', 'KongoBoys', 'Last Order', 'LittleBunny Land', 'Lux Nova', 'Nefarious Ravens', 'Nerfuria', 'Opus Maximus', 'Paladins United', 'Profession Heaven', 'Question Mark Syndicate', 'SICA Team', 'ShadowFall', 'Sins of Seedia', 'Skuc Nation', 'Syndicate of Nyx', 'TVietNam', 'Tartarus Wrath', 'The Aquarium', 'The Broken Gasmask', 'The Dark Phoenix', 'The Mage Legacy', 'The Simple Ones', 'TheNoLifes', 'Titans Valor', 'TruthSworD', 'Wheres The Finish', 'WynnFairyTail', 'busted moments']}
        results = await asyncio.gather(*[fetch(players, bot.session, guild) for guild in guilds])
        
        for res in results:
            if res is not None:
                guilds.update(res)

        time = datetime.utcnow()
        interval = 300
        seconds = (time.replace(tzinfo = None) - time.min).seconds
        difference = (seconds + interval / 2) // interval * interval - seconds
        rounded_time = str(time + timedelta(0, difference, -time.microsecond))

        columns = '`, `'.join(guilds.keys())
        placeholders = '%s' + ', %s' * len(guilds)
        sql = f'INSERT INTO guildActivity(`time`, `{columns}`) VALUES ({placeholders})'
        values = (rounded_time, *guilds.values())

        try:
            bot.query(sql, values)
        except:
            print('Duplicate guild activity time')

async def fetch(player_list, session, guild):
    async with session.get(f'https://api.wynncraft.com/public_api.php?action=guildStats&command={guild}') as response:
        response = await response.json()
        try:
            return {guild: sum(player['name'] in player_list for player in response['members'])}
        except KeyError:
            print('Error when fetching ' + guild + '\'s activity!')