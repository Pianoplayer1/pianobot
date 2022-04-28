from uuid import uuid4

from corkus.errors import BadRequest
from discord import Embed, Interaction, app_commands
from discord.ext import commands

from pianobot import Pianobot


class LegacyPlayerActivity(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        aliases=['pAct'],
        brief='Outputs the activity of a given player in a given interval.',
        help=(
            'This command returns a bar graph with the number of minutes a given player has been'
            ' online in the last days.'
        ),
        name='playerActivity',
        usage='<player> [days]',
    )
    async def pact(self, ctx: commands.Context, player: str, interval: str = '14') -> None:
        await ctx.send(
            '```prolog\nNote: this command has been updated with a slash command version:\n     '
            ' \'/pact <player> [days]\' is the new way to access player activity charts.\n     '
            ' \'-pAct <player> [interval]\' (the command you just used) will only work for'
            ' limited time.```'
        )
        if interval.startswith('-'):
            interval = interval[1:]
        try:
            int_interval = int(interval)
        except ValueError:
            await ctx.send('Please provide a valid interval!')
            return
        embed = Embed()
        embed.set_author(icon_url=f'https://mc-heads.net/head/{player}.png', name=player)
        embed.set_image(
            url=(
                'https://wynnstats.dieterblancke.xyz/api/charts'
                f'/onlinetime/{player}/{int_interval}?caching={uuid4()}'
            )
        )
        embed.set_footer(text='Player tracking from \'WynnStats\' by Dieter Blancke')
        await ctx.send(embed=embed)


class PlayerActivity(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @app_commands.command(description='Activity of a Wynncraft player in a set interval')
    @app_commands.describe(
        player='Username of the player to get activity for',
        days='How many days the data should go back',
    )
    async def pact(self, interaction: Interaction, player: str, days: int = 14) -> None:
        try:
            wynn_player = await self.bot.corkus.player.get(player)
        except BadRequest:
            await interaction.response.send_message('Not a valid Wynncraft player!')
            return

        embed = Embed()
        embed.set_author(
            icon_url=f'https://mc-heads.net/head/{wynn_player.username}.png',
            name=wynn_player.username,
        )
        embed.set_image(
            url=(
                'https://wynnstats.dieterblancke.xyz/api/charts'
                f'/onlinetime/{wynn_player.username}/{days}?caching={uuid4()}'
            )
        )
        embed.set_footer(text='Player tracking from \'WynnStats\' by Dieter Blancke')
        await interaction.response.send_message(embed=embed)


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(LegacyPlayerActivity(bot))
    await bot.add_cog(PlayerActivity(bot))
