from datetime import datetime
from math import floor, log10

from discord.ext import commands

from ..bot import Pianobot
from ..utils.pages import paginator
from ..utils.table import table

class GuildXP(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(name='gxp',
                      aliases=['guildXP'],
                      brief='Outputs guild experience in a specified interval.',
                      help='This command returns a list with the amount of guild experience members of Eden have gained in a specified interval (defaults to 7 days).',
                      usage='-[unit] [interval]')
    async def gxp(self, ctx: commands.Context, unit: str = '-d', interval: int = 7):
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
        pos = max(0, min(len(names) - 1, int(floor(0 if n == 0 else log10(abs(n)) / 3))))
        return f'{round(n / 10 ** (3 * pos), 2):g}{names[pos]}'

def setup(bot: Pianobot):
    bot.add_cog(GuildXP(bot))
