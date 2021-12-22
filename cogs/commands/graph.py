from discord import File
from discord.ext import commands

from matplotlib import dates, pyplot

from ..bot import Pianobot

class Graph(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(name='graph',
                      brief='Outputs the member activity of a guild as a line graph.',
                      help='This command returns a line graph with the number of members online in the last days.',
                      usage='<guild> -[days]')
    async def graph(self, ctx: commands.Context, *, guild: str):
        interval: int = 1
        if '-' in guild:
            guild, interval = guild.split(' -')
            try:
                interval = int(interval)
            except TypeError:
                await ctx.send('Interval must be a number!')
                return

        guilds = {'Cyphrus Code': 'CYX', 'ShadowFall': 'Shy', 'Question Mark Syndicate': 'QMS', 'Gabameno': 'GBE', 'Wheres The Finish': 'WFN', 'Breadskate': 'BSE', 'Jasmine Dragon': 'LEAF', 'Eden': 'EDN', 'Avicia': 'AVO', 'Atlas Inc': 'AIn', 'Nerfuria': 'Nia', 'LittleBunny Land': 'LBL', 'The Broken Gasmask': 'TBGM', 'Opus Maximus': 'OpM', 'Tartarus Wrath': 'Fate', 'WynnFairyTail': 'WFT', 'Syndicate of Nyx': 'SYNN', 'Emorians': 'ERN', 'ForsakenLaws': 'FKL', 'Skuc Nation': 'skuc', 'The Simple Ones': 'ILQ', 'Lux Nova': 'LXA', 'Forever Twilight': 'FXX', 'Guardian of Wynn': 'GsW', 'Idiot Co': 'ICo', 'Crystal Iris': 'Cona', 'Last Order': 'IPS', 'Kingdom Foxes': 'Fox', 'Jeus': 'Jeus', 'The Aquarium': 'TAq', 'Germany': 'DEU', 'Titans Valor': 'ANO', 'Empire of Sindria': 'ESI', 'FlameKnights': 'FLK', 'Nefarious Ravens': 'NFR', 'KongoBoys': 'DUDE', 'Blacklisted': 'BLA', 'TVietNam': 'VNP', 'Gopniks': 'GKS', 'Profession Heaven': 'PROF', 'TruthSworD': 'Tsd', 'IceBlue Team': 'IBT', 'busted moments': 'fuy', 'HackForums': 'Hax', 'Sins of Seedia': 'SDU', 'Fuzzy Spiders': 'cxz', 'The Mage Legacy': 'Mag', 'The Dark Phoenix': 'TNI', 'Aequitas': 'Aeq', 'TheNoLifes': 'TNL', 'Paladins United': 'PUN', 'Achte Shadow': 'ASh', 'SICA Team': 'FEU'}
        matches = [k for k, v in guilds.items() if k.lower() == guild.lower() or v.lower() == guild.lower()]
        if len(matches) == 0:
            await ctx.send(f'`{guild}` is not a tracked guild!')
            return
        guild = matches[0]

        data = self.bot.db.guild_activity.get(guild, interval)

        plot, axes = pyplot.subplots()
        axes.plot(data.keys(), data.values())
        axes.xaxis.set_major_formatter(dates.DateFormatter('%b %d, %H:%M'))
        axes.xaxis.set_label_position('top')
        plot.autofmt_xdate()
        pyplot.xlabel(f'Online Player Activity of {guild} [{guilds[guild]}]')
        pyplot.ylabel('Player Count')
        plot.savefig('graph.png')

        await ctx.send(file = File('graph.png'))

def setup(bot: Pianobot):
    bot.add_cog(Graph(bot))
