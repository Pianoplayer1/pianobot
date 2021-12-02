from datetime import datetime
from discord.ext import commands
import discord
from functions.db import query
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
        
        guild_list = ['Achte Shadow', 'Aequitas', 'Atlas Inc', 'Avicia', 'Blacklisted', 'Breadskate', 'Crystal Iris', 'Cyphrus Code', 'Eden', 'Emorians', 'Empire of Sindria', 'FlameKnights', 'Forever Twilight', 'ForsakenLaws', 'Fuzzy Spiders', 'Gabameno', 'Germany', 'Gopniks', 'Guardian of Wynn', 'HackForums', 'IceBlue Team', 'Idiot Co', 'Jasmine Dragon', 'Jeus', 'Kingdom Foxes', 'KongoBoys', 'Last Order', 'LittleBunny Land', 'Lux Nova', 'Nefarious Ravens', 'Nerfuria', 'Opus Maximus', 'Paladins United', 'Profession Heaven', 'Question Mark Syndicate', 'SICA Team', 'ShadowFall', 'Sins of Seedia', 'Skuc Nation', 'Syndicate of Nyx', 'TVietNam', 'Tartarus Wrath', 'The Aquarium', 'The Broken Gasmask', 'The Dark Phoenix', 'The Mage Legacy', 'The Simple Ones', 'TheNoLifes', 'Titans Valor', 'TruthSworD', 'Wheres The Finish', 'WynnFairyTail', 'busted moments']
        guilds = [g for g in guild_list if g.lower() == guild.lower()]
        if len(guilds) != 1:
            await ctx.send(f'`{guild}` is not a tracked guild!')
            return
        guild = guilds[0]

        res = query(f"SELECT time, `{guild}` FROM `guildActivity` WHERE `time` > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL {interval} DAY);")
        data = {time : amount for time, amount in res}
        
        plot, axes = pyplot.subplots()
        axes.plot(data.keys(), data.values())
        axes.xaxis.set_major_formatter(dates.DateFormatter('%b %d, %H:%M'))
        axes.xaxis.set_label_position('top')
        plot.autofmt_xdate()
        pyplot.xlabel('Online Player Activity')
        pyplot.ylabel('Player Count')

        plot.savefig('graph.png')
        await ctx.send(file=discord.File(r'graph.png'))

def setup(client):
    client.add_cog(Graph(client))