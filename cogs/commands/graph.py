from datetime import datetime
from discord.ext import commands
import discord
from matplotlib import pyplot, dates

class Graph(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(  name = 'graph',
                        brief = 'Outputs the member activity of a guild as a line graph.',
                        help = 'This command returns a line graph with the number of members online in the last days.',
                        usage = '<guild>'  )
    async def graph(self, ctx : commands.Context, *, guild : str):
        interval = 7
        try:
            if '-' in guild:
                guild, interval = guild.split(' -')
                interval = int(interval)
        except Exception:
            await ctx.send('Interval must be a number!')
            return
        
        guild_list = {'Cyphrus Code': 'CYX', 'ShadowFall': 'Shy', 'Question Mark Syndicate': 'QMS', 'Gabameno': 'GBE', 'Wheres The Finish': 'WFN', 'Breadskate': 'BSE', 'Jasmine Dragon': 'LEAF', 'Eden': 'EDN', 'Avicia': 'AVO', 'Atlas Inc': 'AIn', 'Nerfuria': 'Nia', 'LittleBunny Land': 'LBL', 'The Broken Gasmask': 'TBGM', 'Opus Maximus': 'OpM', 'Tartarus Wrath': 'Fate', 'WynnFairyTail': 'WFT', 'Syndicate of Nyx': 'SYNN', 'Emorians': 'ERN', 'ForsakenLaws': 'FKL', 'Skuc Nation': 'skuc', 'The Simple Ones': 'ILQ', 'Lux Nova': 'LXA', 'Forever Twilight': 'FXX', 'Guardian of Wynn': 'GsW', 'Idiot Co': 'ICo', 'Crystal Iris': 'Cona', 'Last Order': 'IPS', 'Kingdom Foxes': 'Fox', 'Jeus': 'Jeus', 'The Aquarium': 'TAq', 'Germany': 'DEU', 'Titans Valor': 'ANO', 'Empire of Sindria': 'ESI', 'FlameKnights': 'FLK', 'Nefarious Ravens': 'NFR', 'KongoBoys': 'DUDE', 'Blacklisted': 'BLA', 'TVietNam': 'VNP', 'Gopniks': 'GKS', 'Profession Heaven': 'PROF', 'TruthSworD': 'Tsd', 'IceBlue Team': 'IBT', 'busted moments': 'fuy', 'HackForums': 'Hax', 'Sins of Seedia': 'SDU', 'Fuzzy Spiders': 'cxz', 'The Mage Legacy': 'Mag', 'The Dark Phoenix': 'TNI', 'Aequitas': 'Aeq', 'TheNoLifes': 'TNL', 'Paladins United': 'PUN', 'Achte Shadow': 'ASh', 'SICA Team': 'FEU'}
        guilds = [k for k, v in guild_list.items() if k.lower() == guild.lower() or v.lower() == guild.lower()]
        if len(guilds) != 1:
            await ctx.send(f'`{guild}` is not a tracked guild!')
            return
        guild = guilds[0]

        res = self.client.query(f"SELECT time, `{guild}` FROM `guildActivity` WHERE `time` > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL {interval} DAY);")
        data = {time : amount for time, amount in res}
        
        plot, axes = pyplot.subplots()
        axes.plot(data.keys(), data.values())
        axes.xaxis.set_major_formatter(dates.DateFormatter('%b %d, %H:%M'))
        axes.xaxis.set_label_position('top')
        plot.autofmt_xdate()
        pyplot.xlabel(f'Online Player Activity of {guild} [{guild_list[guild]}]')
        pyplot.ylabel('Player Count')

        plot.savefig('graph.png')
        await ctx.send(file=discord.File(r'graph.png'))

def setup(client):
    client.add_cog(Graph(client))