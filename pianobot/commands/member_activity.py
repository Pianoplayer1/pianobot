from datetime import datetime

from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import legacy_paginator
from pianobot.utils import table


class MemberActivity(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        aliases=['mAct'],
        brief='Outputs the member activity times of Eden for a calendar week.',
        help=(
            'This command returns a table with the times each member of Eden has been active on'
            ' the Wynncraft server. Optionally, use a week number and a year to get activity times'
            ' of a certain week.'
        ),
        name='memberActivity',
        usage='[calendar week] [year]',
    )
    async def member_activity(
        self, ctx: commands.Context, week: int | None = None, year: int | None = None
    ) -> None:
        iso_date = datetime.utcnow().isocalendar()
        if week is None:
            week = iso_date.week
        if year is None:
            year = iso_date.year
        date = f'{year}-{week}'
        if date not in await self.bot.database.member_activity.get_weeks():
            await ctx.send('No data available for the specified interval!')
            return

        results = []
        guild = await self.bot.corkus.guild.get('Eden')
        for username, time in (await self.bot.database.member_activity.get(date)).items():
            member = next(
                (member for member in guild.members if member.username == username), None
            )
            results.append(
                (
                    time,
                    (
                        username,
                        'Unknown' if member is None else member.rank.value.title(),
                        f'{time} minutes'
                        if time < 60
                        else f'{int(time / 60):02}:{time % 60:02} hours',
                    ),
                )
            )

        columns = {'Eden Members': 36, 'Rank': 26, 'Time Online': 26}
        result = [list(res[1]) for res in sorted(results, key=lambda item: item[0])]
        ascending_table = table(columns, result, 5, 15, True, '(Ascending Order)')
        result.reverse()
        descending_table = table(columns, result, 5, 15, True, '(Descending Order)')
        await legacy_paginator(self.bot, ctx, descending_table, None, ascending_table)


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(MemberActivity(bot))
