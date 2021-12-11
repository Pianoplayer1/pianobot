from ..bot import Pianobot
from ..utils.pages import paginator
from ..utils.table import table
from discord.ext import commands
from datetime import datetime
import math

class GuildXP(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot

    @commands.command(  name = 'gxp',
                        aliases = ['guildXP'],
                        brief = 'Outputs guild experience in a specified interval.',
                        help = 'This command returns a list with the amount of guild experience members of Eden have gained in a specified interval (defaults to 7 days).',
                        usage = '-[unit] [interval]')
    async def gxp(self, ctx : commands.Context, unit : str = '-d', interval : int = 7):
        if unit.startswith('-'):
            unit = unit[1:]
        units = {'m': 'minute', 'h': 'hour', 'd': 'day', 'w': 'week'}
        if unit.lower() not in units.keys():
            await ctx.send('Not a valid time unit!')
            return
        unit = units[unit.lower()]


        columns = [column[0] for column in self.bot.query('SELECT "column_name" FROM "information_schema"."columns" WHERE "table_name" = \'guildXP\';')]
        oldest_data = self.bot.query(f'SELECT * FROM "guildXP" WHERE time > (CURRENT_TIMESTAMP - \'{interval} {unit}\'::interval) LIMIT 1;')
        newest_data = self.bot.query('SELECT * FROM "guildXP" ORDER BY time DESC LIMIT 2;')
        if len(oldest_data) == 0 or oldest_data[0] == newest_data[0]:
            oldest_data = newest_data[1]
        else:
            oldest_data = oldest_data[0]
        newest_data = newest_data[0]
        start_time = round((oldest_data[0] - datetime(1970, 1, 1)).total_seconds())
        end_time = round((newest_data[0] - datetime(1970, 1, 1)).total_seconds())
        differences = {columns[i]: newest_data[i] - oldest_data[i] for i in range(1, len(columns))}

        table_cols = {f'Eden Members': 36, f'Gained Guild XP': 30}
        ascending_data = [[name, self.format(xp)] for name, xp in sorted(differences.items(), key = lambda item: item[1])]
        descending_data = [[name, self.format(xp)] for name, xp in sorted(differences.items(), key = lambda item: item[1], reverse=True)]
        ascending_table = table(table_cols, ascending_data, 5, 15, True, '(Ascending Order)', f'Guild XP data from **<t:{start_time}> to <t:{end_time}>**')
        descending_table = table(table_cols, descending_data, 5, 15, True, '(Descending Order)', f'Guild XP data from **<t:{start_time}> to <t:{end_time}>**')
        await paginator(self.bot, ctx, descending_table, None, ascending_table)
    
    def format(self, n : float):
        names = ['',' Thousand',' Million',' Billion',' Trillion']
        pos = max(0, min(len(names) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
        return f'{n / 10 ** (3 * pos):.2f}{names[pos]}'

def setup(bot : Pianobot):
    bot.add_cog(GuildXP(bot))