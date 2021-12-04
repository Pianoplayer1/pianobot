from discord.ext import commands
import discord
from functions.db import query
from matplotlib import pyplot, dates

class PlayerActivity(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(  name = 'playerActivity',
                        aliases = ['pAct'],
                        brief = 'Outputs the activity of a given player in a given interval.',
                        help = 'This command returns a bar graph with the number of minutes a given player has been online in the last days.',
                        usage = '<player> [days]'  )
    async def graph(self, ctx : commands.Context, player : str, interval : int = 14):
        res = query(f"SELECT `date`, `count` FROM `playerActivity` WHERE `name` = CONCAT(`date`, '_{player}') AND `date` > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL {interval} DAY);")

        data = {time : amount for time, amount in res}
        
        plot, axes = pyplot.subplots()
        #times = [str(key) for key in data.keys()]
        bar = axes.bar(data.keys(), data.values())
        axes.xaxis.set_major_locator(dates.DayLocator(interval=1))  
        axes.xaxis.set_major_formatter(dates.DateFormatter('%a'))
        axes.xaxis.set_label_position('top')
        axes.bar_label(bar, label_type='center', color='white')
        pyplot.xlabel(f'Player Activity of {player}')
        pyplot.ylabel('Minutes')

        plot.savefig('pact.png')
        await ctx.send(file=discord.File(r'pact.png'))

def setup(client):
    client.add_cog(PlayerActivity(client))