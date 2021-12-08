from ..bot import Pianobot
from ..utils.pages import paginator
from ..utils.table import table
from discord.ext import commands

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
        oldest_data = self.bot.query(f'SELECT * FROM "guildXP" WHERE time > (CURRENT_TIMESTAMP - \'{interval} {unit}\'::interval) LIMIT 1;')[0]
        newest_data = self.bot.query('SELECT * FROM "guildXP" ORDER BY time DESC LIMIT 1;')[0]
        differences = {columns[i]: newest_data[i] - oldest_data[i] for i in range(1, len(columns))}

        table_cols = {f'Eden Members' : 36, f'Guild XP Since {str(oldest_data[0])[:-3]} UTC' : 40}
        ascending_data = [[name, xp] for name, xp in sorted(differences.items(), key = lambda item: item[1])]
        descending_data = [[name, xp] for name, xp in sorted(differences.items(), key = lambda item: item[1], reverse=True)]
        ascending_table = table(table_cols, ascending_data, 5, 15, True, '(Ascending Order)')
        descending_table = table(table_cols, descending_data, 5, 15, True, '(Descending Order)')
        await paginator(self.bot, ctx, descending_table, None, ascending_table)

def setup(bot : Pianobot):
    bot.add_cog(GuildXP(bot))