import math
from datetime import datetime, timedelta

from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import paginator
from pianobot.utils import table


class GXP(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        aliases=['guildXP', 'xp'],
        brief='Outputs Eden\'s guild experience contributions in a set interval.',
        help=(
            'This command returns a list with the amount of guild experience members of Eden have'
            ' gained in the current or, if specified with `final`, the last week. For custom'
            ' intervals, provide a unit specifier (such as `d` for day) and a number (e.g. `3`)'
            ' after the command (the previous examples would form the command `[[prefix]] gxp d 3`'
            ' and thus give out the guild experience gained in the last three days).'
        ),
        name='gxp',
        usage='["final" | custom interval]',
    )
    async def gxp(self, ctx: commands.Context, unit: str = '', interval: int = 1) -> None:
        first_weekday = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        first_weekday = first_weekday - timedelta(days=first_weekday.weekday())

        if unit == '':
            oldest_data = self.bot.database.guild_xp.get(first_weekday)
            last_data = self.bot.database.guild_xp.get_last()
            if len(last_data) == 0:
                newest_data = None
            else:
                newest_data = last_data[0]
        elif unit == 'final':
            oldest_data = self.bot.database.guild_xp.get(first_weekday - timedelta(days=7))
            newest_data = self.bot.database.guild_xp.get(first_weekday)
        else:
            if unit.startswith('-'):
                unit = unit[1:]
            formatted_unit = {'m': 'minute', 'h': 'hour', 'd': 'day', 'w': 'week'}.get(
                unit.lower()
            )
            if formatted_unit is None:
                await ctx.send('Not a valid time unit!')
                return

            oldest_data = self.bot.database.guild_xp.get_first(f'{interval} {formatted_unit}')
            recent_data = self.bot.database.guild_xp.get_last(2)
            if oldest_data is None or oldest_data.time == recent_data[0].time:
                oldest_data = recent_data[1]
            newest_data = recent_data[0]
        if oldest_data is None or newest_data is None:
            await ctx.send('No data could be found. Try again later!')
            return

        time = (
            f'<t:{round((oldest_data.time - datetime(1970, 1, 1)).total_seconds())}>'
            f' - <t:{round((newest_data.time - datetime(1970, 1, 1)).total_seconds())}>'
        )
        differences = [
            [name, display(xp)]
            for name, xp in sorted(
                [(m, newest_data.data[m] - xp) for m, xp in oldest_data.data.items()],
                key=lambda item: item[1],
            )
        ]

        table_cols = {'Eden Members': 36, 'Gained Guild XP': 30}
        ascending_table = table(table_cols, differences, 5, 15, True, '(Ascending Order)', time)
        differences.reverse()
        descending_table = table(table_cols, differences, 5, 15, True, '(Descending Order)', time)
        await paginator(self.bot, ctx, descending_table, None, ascending_table)


def display(num: int | float) -> str:
    names = ['', ' Thousand', ' Million', ' Billion', ' Trillion']
    pos = max(
        0,
        min(len(names) - 1, int(math.floor(0 if num == 0 else math.log10(abs(num)) / 3))),
    )
    return f'{num / 10 ** (3 * pos):.2f}{names[pos]}'


def setup(bot: Pianobot) -> None:
    bot.add_cog(GXP(bot))
