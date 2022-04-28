from discord import File, Interaction, app_commands
from discord.ext import commands
from matplotlib import dates, pyplot

from pianobot import Pianobot


class LegacyGraph(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        brief='Outputs the member activity of a guild as a line graph.',
        help=(
            'This command returns a line graph with the number of members online in the last days.'
        ),
        name='graph',
        usage='<guild> -[days]',
    )
    async def graph(self, ctx: commands.Context, *, input_guild: str) -> None:
        await ctx.send(
            '```prolog\nNote: this command has been updated with a slash command version:\n     '
            ' \'/graph <guild> [days]\' is the new way to access activity graphs.\n      \'-graph'
            ' <guild> -[interval]\' (the command you just used) will only work for limited'
            ' time.```'
        )
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
            await ctx.send(f'`{input_guild}` is not a tracked guild!')
            return

        await generate_graph(self.bot, guild, interval)
        await ctx.send(file=File('graph.png'))


async def generate_graph(bot: Pianobot, guild: str, days: int):
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


class Graph(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @app_commands.command(description='Member activity of a guild as a line graph')
    @app_commands.describe(
        input_guild='Name or prefix of the guild to check activity for',
        days='How many days the data should go back',
    )
    @app_commands.rename(input_guild='guild')
    async def graph(self, interaction: Interaction, input_guild: str, days: int = 1):
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
            if interaction.guild is not None:
                guild_member = interaction.guild.get_member(667445845792391208)
                if guild_member is not None:
                    member = guild_member.mention
            await interaction.response.send_message(
                f'`{input_guild}` is not a tracked guild! If you want your guild activity to be'
                f' tracked, message {member}.'
            )
            return

        await generate_graph(self.bot, guild, days)
        await interaction.response.send_message(file=File('graph.png'))


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(LegacyGraph(bot))
    await bot.add_cog(Graph(bot))
