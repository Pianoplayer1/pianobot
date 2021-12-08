from ..bot import Pianobot
from discord.ext import commands
from discord import File
from matplotlib import pyplot, dates

class PlayerActivity(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot

    @commands.command(  name = 'playerActivity',
                        aliases = ['pAct'],
                        brief = 'Outputs the activity of a given player in a given interval.',
                        help = 'This command returns a bar graph with the number of minutes a given player has been online in the last days.',
                        usage = '<player> [days]')
    async def graph(self, ctx : commands.Context, player : str, interval : int = 14):
        res = self.bot.query(f'SELECT `date`, `count` FROM `playerActivity` WHERE `name` = CONCAT(`date`, \'_{player}\') AND `date` > (CURRENT_TIMESTAMP - \'{interval} day\'::interval);')
        data = {time: amount for time, amount in res}

        plot, axes = pyplot.subplots()
        bar = axes.bar(data.keys(), data.values())
        axes.xaxis.set_major_locator(dates.DayLocator(interval=1))  
        axes.xaxis.set_major_formatter(dates.DateFormatter('%a'))
        axes.xaxis.set_label_position('top')
        axes.bar_label(bar, label_type='center', color='white')
        pyplot.xlabel(f'Player Activity of {player}')
        pyplot.ylabel('Minutes')
        plot.savefig('pact.png')

        await ctx.send(file = File('pact.png'))

def setup(bot : Pianobot):
    bot.add_cog(PlayerActivity(bot))