from discord import File
from discord.ext import commands

from matplotlib import dates, pyplot

from pianobot import Pianobot

class Graph(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(
        brief='Outputs the member activity of a guild as a line graph.',
        help=
            'This command returns a line graph with the number of members'
            ' online in the last days.',
        name='graph',
        usage='<guild> -[days]'
    )
    async def graph(self, ctx: commands.Context, *, input_guild: str):
        interval: int = 1
        if '-' in input_guild:
            input_guild, interval = input_guild.split(' -')
            try:
                interval = int(interval)
            except ValueError:
                await ctx.send('Interval must be a number!')
                return

        guild = next(
            (k for k, v in self.bot.tracked_guilds.items()
                if k.lower() == input_guild.lower() or v.lower() == input_guild.lower()),
            None
        )
        if guild is None:
            await ctx.send(f'`{input_guild}` is not a tracked guild!')
            return

        data = self.bot.database.guild_activity.get(guild, interval)

        plot, axes = pyplot.subplots()
        axes.plot(data.keys(), data.values())
        axes.xaxis.set_major_formatter(dates.DateFormatter('%b %d, %H:%M'))
        axes.xaxis.set_label_position('top')
        plot.autofmt_xdate()
        pyplot.xlabel(f'Online Player Activity of {guild} [{self.bot.tracked_guilds[guild]}]')
        pyplot.ylabel('Player Count')
        plot.savefig('graph.png')

        await ctx.send(file=File('graph.png'))

def setup(bot: Pianobot):
    bot.add_cog(Graph(bot))
