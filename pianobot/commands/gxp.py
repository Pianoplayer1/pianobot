import math
from datetime import datetime, timedelta, timezone

from discord.ext.commands import Bot, Cog, Context, command
from discord.utils import format_dt

from pianobot import Pianobot
from pianobot.utils import paginator


class GXP(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @command(
        aliases=['guildXP', 'xp'],
        brief='Outputs Eden\'s guild experience contributions in a set interval.',
        help=(
            'This command returns a list with the amount of guild experience members of Eden have'
            ' gained in the current or, if specified with `final`, the last week. For custom'
            ' intervals, provide a unit specifier (such as `d` for day) and a number (e.g. `3`)'
            ' after the command (the previous examples would form the command `[[prefix]]gxp d 3`'
            ' and thus give out the guild experience gained in the last three days).'
        ),
        name='gxp',
        usage='["final" | custom interval]',
    )
    async def gxp(self, ctx: Context[Bot], unit: str = '', interval: int = 1) -> None:
        current_day = datetime.combine(datetime.utcnow(), datetime.min.time(), timezone.utc)
        first_weekday = current_day - timedelta(days=current_day.weekday())

        if unit == '':
            oldest_data = await self.bot.database.guild_xp.get(first_weekday)
            last_data = await self.bot.database.guild_xp.get_last()
            if len(last_data) == 0:
                newest_data = None
            else:
                newest_data = last_data[0]
        elif unit == 'final':
            oldest_data = await self.bot.database.guild_xp.get(first_weekday - timedelta(days=7))
            newest_data = await self.bot.database.guild_xp.get(first_weekday)
        else:
            if unit.startswith('-'):
                unit = unit[1:]
            formatted_unit = {'m': 'minute', 'h': 'hour', 'd': 'day', 'w': 'week'}.get(
                unit.lower()
            )
            if formatted_unit is None:
                await ctx.send('Not a valid time unit!')
                return

            oldest_data = await self.bot.database.guild_xp.get_first(
                f'{interval} {formatted_unit}'
            )
            recent_data = await self.bot.database.guild_xp.get_last(2)
            if oldest_data is None or oldest_data.time == recent_data[0].time:
                oldest_data = recent_data[1]
            newest_data = recent_data[0]
        if oldest_data is None or newest_data is None:
            await ctx.send('No data could be found. Try again later!')
            return

        xp_diff = []
        for name, new_xp in newest_data.data.items():
            old_xp = oldest_data.data.get(name, None)
            if new_xp is not None and old_xp is not None:
                xp_diff.append((name, new_xp - old_xp))
        results = [[name, display(xp)] for name, xp in sorted(xp_diff, key=lambda item: item[1])]

        await ctx.send(f'{format_dt(oldest_data.time)} - {format_dt(newest_data.time)}')
        columns = {'Eden Members': 36, 'Gained Guild XP': 30}
        await paginator(ctx, results, columns)


def display(num: int | float) -> str:
    names = ['', ' Thousand', ' Million', ' Billion', ' Trillion']
    pos = max(
        0,
        min(len(names) - 1, int(math.floor(0 if num == 0 else math.log10(abs(num)) / 3))),
    )
    return f'{num / 10 ** (3 * pos):.2f}{names[pos]}'


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(GXP(bot))
