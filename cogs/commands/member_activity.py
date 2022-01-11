from asyncio import gather, sleep
from datetime import datetime, timezone

from corkus.objects import Member

from discord import Message
from discord.ext import commands

from ..bot import Pianobot
from ..utils.pages import paginator
from ..utils.permissions import check_permissions
from ..utils.table import table

class MemberActivity(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(name='memberActivity',
                      aliases=['mAct'],
                      brief='Outputs the member activity times of Eden for a calendar week.',
                      help='This command returns a table with the times each member of Eden has been active on the Wynncraft server. Optionally, use a week number and a year to get activity times of a certain week.',
                      usage='[week] [year]')
    async def member_activity(self, ctx: commands.Context, week: int = None, year: int = None):
        iso_date = datetime.utcnow().isocalendar()
        if week is None:
            week = iso_date.week
        if year is None:
            year = iso_date.year
        date = f'{year}-{week}'
        if date not in self.bot.db.member_activity.get_weeks():
            await ctx.send('No data avilable for the specified interval!')
            return
        
        results = []
        guild = await self.bot.corkus.guild.get('Eden')
        for username, minutes in self.bot.db.member_activity.get(date).items():
            rank = 'Unknown'
            member = [member for member in guild.members if member.username == username]
            if len(member) > 0:
                rank = member[0].rank.value.title()
            
            display_time = f'{minutes} minutes'
            if minutes >= 60:
                display_time = f'{int(minutes / 60):02}:{minutes % 60:02} hours'
            
            results.append([minutes, [username, rank, display_time]])

        columns = {f'Eden Members' : 36, 'Rank' : 26, 'Time Online' : 26}
        ascending_data = [result[1] for result in sorted(results, key = lambda item: item[0])]
        descending_data = [result[1] for result in sorted(results, key = lambda item: item[0], reverse=True)]
        ascending_table = table(columns, ascending_data, 5, 15, True, '(Ascending Order)')
        descending_table = table(columns, descending_data, 5, 15, True, '(Descending Order)')
        await paginator(self.bot, ctx, descending_table, None, ascending_table)

def setup(bot: Pianobot):
    bot.add_cog(MemberActivity(bot))
