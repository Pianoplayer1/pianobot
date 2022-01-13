from uuid import uuid4

from discord import Embed
from discord.ext import commands

from pianobot import Pianobot

class PlayerActivity(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(
        aliases = ['pAct'],
        brief = 'Outputs the activity of a given player in a given interval.',
        help = 'This command returns a bar graph with the number of minutes'
            ' a given player has been online in the last days.',
        name = 'playerActivity',
        usage = '<player> [days]'
    )
    async def graph(self, ctx: commands.Context, player: str, interval: str = '14'):
        if interval.startswith('-'):
            interval = interval[1:]
        try:
            interval = int(interval)
        except ValueError:
            await ctx.send('Please provide a valid interval!')
            return
        embed = Embed()
        embed.set_author(icon_url = f'https://mc-heads.net/head/{player}.png', name = player)
        embed.set_image(url = (
            'https://wynnstats.dieterblancke.xyz/api/charts'
            f'/onlinetime/{player}/{interval}?caching={uuid4()}'
        ))
        embed.set_footer(text = 'Player tracking from \'WynnStats\' by Dieter Blancke')
        await ctx.send(embed = embed)

def setup(bot: Pianobot):
    bot.add_cog(PlayerActivity(bot))
