from ..bot import Pianobot
from ..utils.pages import paginator
from ..utils.table import table
from discord.ext import commands
from datetime import datetime, timedelta
import math

class GuildXP(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot

    @commands.command(  name = 'xp',
                        brief = 'Outputs guild experience contribution for the current week.',
                        help = 'This command returns a list with the amount of guild experience members of Eden have gained in the current week.',
                        usage = '')
    async def gxp(self, ctx : commands.Context):
        day = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        day = day - timedelta(days = day.weekday())

        columns = [column[0] for column in self.bot.query('SELECT "column_name" FROM "information_schema"."columns" WHERE "table_name" = \'guildXP\';')]
        oldest_data = self.bot.query('SELECT * FROM "guildXP" WHERE time = %s;', day)[0]
        newest_data = self.bot.query('SELECT * FROM "guildXP" ORDER BY time DESC LIMIT 1;')[0]
        start_time = round((oldest_data[0] - datetime(1970, 1, 1)).total_seconds())
        end_time = round((newest_data[0] - datetime(1970, 1, 1)).total_seconds())
        differences = {columns[i]: newest_data[i] - oldest_data[i] for i in range(1, len(columns))}

        table_cols = {f'Eden Members': 36, f'Gained Guild XP': 30}
        ascending_data = [[name, self.format(xp)] for name, xp in sorted(differences.items(), key = lambda item: item[1])]
        descending_data = [[name, self.format(xp)] for name, xp in sorted(differences.items(), key = lambda item: item[1], reverse=True)]
        ascending_table = table(table_cols, ascending_data, 5, 15, True, '(Ascending Order)', f'<t:{start_time}> - <t:{end_time}>')
        descending_table = table(table_cols, descending_data, 5, 15, True, '(Descending Order)', f'<t:{start_time}> - <t:{end_time}>')
        await paginator(self.bot, ctx, descending_table, None, ascending_table)
    
    def format(self, n : float):
        names = ['',' Thousand',' Million',' Billion',' Trillion']
        pos = max(0, min(len(names) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
        return f'{n / 10 ** (3 * pos):.2f}{names[pos]}'

def setup(bot : Pianobot):
    bot.add_cog(GuildXP(bot))