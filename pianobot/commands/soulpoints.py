from math import floor
from time import time

from discord import Interaction, app_commands
from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import table


class LegacySoulpoints(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        aliases=['sp'],
        brief='Returns a list of the next Wynncraft servers that will give you soul points.',
        help=(
            'If you are low on soul points, you can join one of the servers the bot returns to get'
            ' one or two soul points soon. The timers of the bot are not 100% accurate, so if you'
            ' do not get a soul point in the displayed time after joining the server, you may join'
            ' another one from the top of the list.'
        ),
        name='soulpoints',
    )
    async def soulpoints(self, ctx: commands.Context) -> None:
        await ctx.send(
            '```prolog\nNote: this command has been updated with a slash command version:\n     '
            ' \'/soulpoints\' is the new way to access soulpoint tables.\n      \'-soulpoints\''
            ' (the command you just used) will only work for limited time.```'
        )
        data = await get_soulpoint_data(self.bot)
        columns = {'Server': 10, 'Next Soul Point': 18, 'Uptime': 18}
        await ctx.send(table(columns, data[:20])[0])


async def get_soulpoint_data(bot: Pianobot) -> list[tuple[str, str, str]]:
    worlds = [(world.world, world.time) for world in await bot.database.worlds.get_all()]
    now = time()
    worlds = sorted(worlds, key=lambda item: (now - item[1]) % 1200, reverse=True)
    return [
        [
            server,
            f'{floor(20 - ((now - uptime) / 60) % 20):02}:'
            f'{floor((1200 - (now - uptime) % 1200) % 60):02} minutes',
            f'{floor((now - uptime) / 3600):02}:{floor((now - uptime) % 3600 / 60):02} hours',
        ]
        for server, uptime in worlds
    ]


class Soulpoints(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @app_commands.command(
        description='View the next Wynncraft servers that will give you soul points.'
    )
    async def soulpoints(self, interaction: Interaction) -> None:
        data = await get_soulpoint_data(self.bot)
        columns = {'Server': 10, 'Next Soul Point': 18, 'Uptime': 18}
        await interaction.response.send_message(table(columns, data[:20])[0])


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(LegacySoulpoints(bot))
    await bot.add_cog(Soulpoints(bot))
