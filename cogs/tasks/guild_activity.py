from asyncio import gather
from logging import getLogger

from corkus import Corkus
from corkus.objects.online_players import OnlinePlayers

from ..bot import Pianobot

async def run(bot: Pianobot) -> None:
    guilds = {guild: None for guild in ['Achte Shadow', 'Aequitas', 'Atlas Inc', 'Avicia', 'Blacklisted', 'Breadskate', 'Crystal Iris', 'Cyphrus Code', 'Eden', 'Emorians', 'Empire of Sindria', 'FlameKnights', 'Forever Twilight', 'ForsakenLaws', 'Fuzzy Spiders', 'Gabameno', 'Germany', 'Gopniks', 'Guardian of Wynn', 'HackForums', 'IceBlue Team', 'Idiot Co', 'Jasmine Dragon', 'Jeus', 'Kingdom Foxes', 'KongoBoys', 'Last Order', 'LittleBunny Land', 'Lux Nova', 'Nefarious Ravens', 'Nerfuria', 'Opus Maximus', 'Paladins United', 'Profession Heaven', 'Question Mark Syndicate', 'SICA Team', 'ShadowFall', 'Sins of Seedia', 'Skuc Nation', 'Syndicate of Nyx', 'TVietNam', 'Tartarus Wrath', 'The Aquarium', 'The Broken Gasmask', 'The Dark Phoenix', 'The Mage Legacy', 'The Simple Ones', 'TheNoLifes', 'Titans Valor', 'TruthSworD', 'Wheres The Finish', 'WynnFairyTail', 'busted moments']}

    players = await bot.corkus.network.online_players()
    results = await gather(*[fetch(bot.corkus, guild, players) for guild in guilds])

    for res in results:
        if res is not None:
            guilds.update(res)

    bot.db.guild_activity.add(guilds)

async def fetch(corkus: Corkus, guild_name: str, players: OnlinePlayers) -> dict[str, int]:
        guild = await corkus.guild.get(guild_name)
        try:
            return {guild.name: sum(players.is_player_online(member.username) for member in guild.members)}
        except KeyError:
            getLogger('tasks').warning('Error when fetching ' + guild + '\'s activity!')
            return {}
