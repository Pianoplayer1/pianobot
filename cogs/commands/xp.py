from datetime import datetime, timedelta
import math

from discord.ext import commands

from ..bot import Pianobot
from ..utils.pages import paginator
from ..utils.table import table

class XP(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(name='xp',
                      brief='Outputs Eden\'s guild experience contributions in a set interval.',
                      help='This command returns a list with the amount of guild experience members of Eden have gained in the current or, if specified with `final`, the last week. For custom intervals, provide a unit specifier (such as `d` for day) and a number (e.g. `3`) after the command (the previous examples would form the command `xp d 3` and thus give out the guild experience gained in three days).',
                      usage='[final | ::custom interval::]',
                      aliases=['guildXP', 'gxp'])
    async def xp(self, ctx: commands.Context, unit: str = '', interval: int = 1):
        first_weekday = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        first_weekday = first_weekday - timedelta(days = first_weekday.weekday())

        if unit == '':
            oldest_data = self.bot.db.guild_xp.get(first_weekday)
            newest_data = self.bot.db.guild_xp.get_last()[0]
        elif unit == 'final':
            oldest_data = self.bot.db.guild_xp.get(first_weekday - timedelta(days = 7))
            newest_data = self.bot.db.guild_xp.get(first_weekday)
        else:
            if unit.startswith('-'):
                unit = unit[1:]
            units = {'m': 'minute', 'h': 'hour', 'd': 'day', 'w': 'week'}
            if unit.lower() not in units.keys():
                await ctx.send('Not a valid time unit!')
                return
            unit = units[unit.lower()]

            oldest_data = self.bot.db.guild_xp.get_first(f'{interval} {unit}')
            newest_data = self.bot.db.guild_xp.get_last(2)
            if not oldest_data or oldest_data.time == newest_data[0].time:
                oldest_data = newest_data[1]
            newest_data = newest_data[0]

        start_time = round((oldest_data.time - datetime(1970, 1, 1)).total_seconds())
        end_time = round((newest_data.time - datetime(1970, 1, 1)).total_seconds())
        differences = {member: newest_data.data[member] - xp for member, xp in oldest_data.data.items()}

        table_cols = {f'Eden Members': 36, f'Gained Guild XP': 30}
        ascending_data = [[name, self.format(xp)] for name, xp in sorted(differences.items(), key = lambda item: item[1])]
        descending_data = [[name, self.format(xp)] for name, xp in sorted(differences.items(), key = lambda item: item[1], reverse=True)]
        ascending_table = table(table_cols, ascending_data, 5, 15, True, '(Ascending Order)', f'<t:{start_time}> - <t:{end_time}>')
        descending_table = table(table_cols, descending_data, 5, 15, True, '(Descending Order)', f'<t:{start_time}> - <t:{end_time}>')
        await paginator(self.bot, ctx, descending_table, None, ascending_table)

    def format(self, n: float):
        names = ['',' Thousand',' Million',' Billion',' Trillion']
        pos = max(0, min(len(names) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
        return f'{n / 10 ** (3 * pos):.2f}{names[pos]}'

def setup(bot: Pianobot):
    bot.add_cog(XP(bot))
