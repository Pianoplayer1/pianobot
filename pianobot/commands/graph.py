from discord import File
from discord.ext.commands import Bot, Cog, Context, command
from matplotlib import dates, pyplot

from pianobot import Pianobot


class LegacyGraph(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @command(
        brief='Outputs the member activity of a guild as a line graph.',
        help=(
            'This command returns a line graph with the number of members online in the last days.'
        ),
        name='graph',
        usage='<guild> -[days]',
    )
    async def graph(self, ctx: Context[Bot], *, input_guild: str) -> None:
        interval = 1
        if '-' in input_guild:
            input_guild, str_interval = input_guild.split(' -')
            try:
                interval = int(str_interval)
            except ValueError:
                await ctx.send('Interval must be a number!')
                return

        guild = next(
            (
                k
                for k, v in self.bot.tracked_guilds.items()
                if k.lower() == input_guild.lower() or v.lower() == input_guild.lower()
            ),
            None,
        )
        if guild is None:
            member = 'Pianoplayer1#5215'
            if ctx.guild is not None:
                guild_member = ctx.guild.get_member(667445845792391208)
                if guild_member is not None:
                    member = guild_member.mention
            await ctx.send(
                f'`{input_guild}` is not a tracked guild! If you want your guild activity to be'
                f' tracked, message {member}.'
            )
            return

        await generate_graph(self.bot, guild, interval)

        await ctx.send(file=File('graph.png'))


async def generate_graph(bot: Pianobot, guild: str, days: int) -> None:
    data = await bot.database.guild_activity.get(guild, f'{days} day')
    plot, axes = pyplot.subplots()
    axes.plot(data.keys(), data.values())
    axes.xaxis.set_major_formatter(dates.DateFormatter('%b %d, %H:%M'))
    axes.xaxis.set_label_position('top')
    plot.autofmt_xdate()
    pyplot.xlabel(
        f'Online Player Activity of {guild} [{bot.tracked_guilds[guild]}] -'
        f' {days} Day{"" if days == 1 else "s"}'
    )
    pyplot.ylabel('Player Count')
    plot.savefig('graph.png')


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(LegacyGraph(bot))
