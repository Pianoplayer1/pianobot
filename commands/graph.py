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
        print(interval)
        
        guilds = ['ShadowFall', 'Avicia', 'IceBlue Team', 'Guardian of Wynn', 'The Mage Legacy', 'Emorians', 'Paladins United', 'Lux Nova', 'HackForums', 'The Aquarium', 'The Simple Ones', 'Empire of Sindria', 'Titans Valor', 'The Dark Phoenix', 'Nethers Ascent', 'Sins of Seedia', 'WrathOfTheFallen', 'busted moments', 'Nefarious Ravens', 'Aequitas', 'Eden', 'KongoBoys', 'Nerfuria']
        guild = [g for g in guilds if g.lower() == guild.lower()]
        if len(guild) != 1:
            await ctx.send(guild + 'is not a valid guild!')
            return
        guild = guild[0]

        res = query(f"SELECT time, {guild} FROM `guildActivity` WHERE `time` > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL {interval} DAY);")
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