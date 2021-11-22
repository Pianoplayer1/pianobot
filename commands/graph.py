from datetime import datetime
from discord.ext import commands
import discord
from functions.db import query
from matplotlib import pyplot, dates

class Inactivity(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(  name = 'graph',
                        brief = 'Outputs the member activity of a guild as a line graph.',
                        help = 'This command returns a line graph with the number of members online in the last days.',
                        usage = '<guild>'  )
    async def graph(self, ctx : commands.Context, *, guild):
        res = query("SELECT time, Eden FROM `guildActivity` WHERE `time` > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 WEEK);")
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
    client.add_cog(Inactivity(client))