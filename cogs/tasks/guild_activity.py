import asyncio
from corkus import Corkus
from ..bot import Pianobot
from datetime import datetime, timedelta
import logging

async def run(bot : Pianobot) -> None:
    guilds = {guild: None for guild in ['Achte Shadow', 'Aequitas', 'Atlas Inc', 'Avicia', 'Blacklisted', 'Breadskate', 'Crystal Iris', 'Cyphrus Code', 'Eden', 'Emorians', 'Empire of Sindria', 'FlameKnights', 'Forever Twilight', 'ForsakenLaws', 'Fuzzy Spiders', 'Gabameno', 'Germany', 'Gopniks', 'Guardian of Wynn', 'HackForums', 'IceBlue Team', 'Idiot Co', 'Jasmine Dragon', 'Jeus', 'Kingdom Foxes', 'KongoBoys', 'Last Order', 'LittleBunny Land', 'Lux Nova', 'Nefarious Ravens', 'Nerfuria', 'Opus Maximus', 'Paladins United', 'Profession Heaven', 'Question Mark Syndicate', 'SICA Team', 'ShadowFall', 'Sins of Seedia', 'Skuc Nation', 'Syndicate of Nyx', 'TVietNam', 'Tartarus Wrath', 'The Aquarium', 'The Broken Gasmask', 'The Dark Phoenix', 'The Mage Legacy', 'The Simple Ones', 'TheNoLifes', 'Titans Valor', 'TruthSworD', 'Wheres The Finish', 'WynnFairyTail', 'busted moments']}
    
    players = await bot.corkus.network.online_players()
    results = await asyncio.gather(*[fetch(bot.corkus, guild, players) for guild in guilds])
    
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
    sql = f'INSERT INTO "guildActivity"(`time`, `{columns}`) VALUES ({placeholders});'
    values = (rounded_time, *guilds.values())

    try:
        bot.query(sql, values)
    except:
        logging.getLogger('tasks').debug('Duplicate guild activity time')

async def fetch(corkus: Corkus, guild, players):
        guild = await corkus.guild.get(guild)
        try:
            return {guild.name: sum(players.is_player_online(member.username) for member in guild.members)}
        except KeyError:
            logging.getLogger('tasks').warning('Error when fetching ' + guild + '\'s activity!')