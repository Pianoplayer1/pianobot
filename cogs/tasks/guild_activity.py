import asyncio
from ..bot import Pianobot
from datetime import datetime, timedelta

guilds = {}

async def run(bot : Pianobot) -> None:
    global guilds

    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=onlinePlayers') as response:
        serverList = await response.json()
        guilds = {guild: None for guild in ['Achte Shadow', 'Aequitas', 'Atlas Inc', 'Avicia', 'Blacklisted', 'Breadskate', 'Crystal Iris', 'Cyphrus Code', 'Eden', 'Emorians', 'Empire of Sindria', 'FlameKnights', 'Forever Twilight', 'ForsakenLaws', 'Fuzzy Spiders', 'Gabameno', 'Germany', 'Gopniks', 'Guardian of Wynn', 'HackForums', 'IceBlue Team', 'Idiot Co', 'Jasmine Dragon', 'Jeus', 'Kingdom Foxes', 'KongoBoys', 'Last Order', 'LittleBunny Land', 'Lux Nova', 'Nefarious Ravens', 'Nerfuria', 'Opus Maximus', 'Paladins United', 'Profession Heaven', 'Question Mark Syndicate', 'SICA Team', 'ShadowFall', 'Sins of Seedia', 'Skuc Nation', 'Syndicate of Nyx', 'TVietNam', 'Tartarus Wrath', 'The Aquarium', 'The Broken Gasmask', 'The Dark Phoenix', 'The Mage Legacy', 'The Simple Ones', 'TheNoLifes', 'Titans Valor', 'TruthSworD', 'Wheres The Finish', 'WynnFairyTail', 'busted moments']}
        await asyncio.gather(*[fetch(serverList, bot.session, guild) for guild in guilds])

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
            bot.query(sql, variables)
        except Exception:
            print('Duplicate guild activity time')

async def fetch(serverList, session, guild):
    global guilds
    async with session.get(f'https://api.wynncraft.com/public_api.php?action=guildStats&command={guild}') as response:
        response = await response.json()
        count = 0
        try:
            count = sum( any(player['name'] in server for server in serverList.values()) for player in response['members'])
        except KeyError:
            print('error when fetching ' + guild + '\'s activity!')

        guilds[guild] = count