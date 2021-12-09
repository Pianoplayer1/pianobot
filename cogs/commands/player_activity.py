from ..bot import Pianobot
from discord.ext import commands
from discord import File

class PlayerActivity(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot

    @commands.command(  name = 'playerActivity',
                        aliases = ['pAct'],
                        brief = 'Outputs the activity of a given player in a given interval.',
                        help = 'This command returns a bar graph with the number of minutes a given player has been online in the last days.',
                        usage = '<player> [days]')
    async def graph(self, ctx : commands.Context, player : str, interval : int = 14):
        await ctx.send(f'https://wynnstats.dieterblancke.xyz/api/charts/onlinetime/{player}/{interval}')

def setup(bot : Pianobot):
    bot.add_cog(PlayerActivity(bot))
