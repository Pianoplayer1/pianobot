from asyncio import gather, sleep
from datetime import datetime, timezone

from corkus.objects import Member

from discord import Message
from discord.ext import commands

from ..bot import Pianobot
from ..utils.pages import paginator
from ..utils.permissions import check_permissions
from ..utils.table import table

class Inactivity(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(name='inactivity',
                      aliases=['act', 'activity', 'inact'],
                      brief='Outputs the member inactivity times of a specified guild.',
                      help='This command returns a table with the times since each member of a specified guild has been last seen on the Wynncraft server.',
                      usage='<guild>')
    async def inactivity(self, ctx: commands.Context, *, guild: str):
        await ctx.trigger_typing()
        guilds = await self.bot.corkus.guild.list_all()
        guilds = [g.name for g in guilds]
        try:
            matches = [guilds[list(map(str.lower, guilds)).index(guild.lower())]]
        except ValueError:
            matches = [g for g in guilds if guild.lower() in g.lower()]
        if len(matches) == 0:
            await ctx.send(f'No guild names include \'{guild}\'. Please try again with a correct guild name.')
            return
        elif len(matches) == 1:
            guild = matches[0]
            message = None
        elif len(matches) <= 5:
            message = f'Several guild names include `{guild}`. Enter the number of one of the following guilds to view their inactivity.\nTo leave this prompt, type `exit`:\n\n'
            message = await ctx.send(message + '\n'.join([f'{match + 1}. {matches[match]}' for match in range(len(matches))]))

            def check(m: Message):
                return m.author == ctx.author and m.channel == ctx.channel

            answer_msg = await self.bot.wait_for('message', check = check)
            if ctx.guild and check_permissions(self.bot.user, ctx.channel, ['manage_messages']):
                await answer_msg.delete()

            try:
                guild = matches[int(answer_msg.content) - 1]
            except (IndexError, ValueError):
                if answer_msg.content == 'exit':
                    await message.edit(content = 'Prompt exited.')
                else:
                    await message.edit(content = 'Invalid input, exited prompt.')
                await sleep(6)
                await message.delete()
                return
        else:
            await ctx.send(f'Several guild names include \'{guild}\'. Please try again with a more precise name.')
            return

        guild_stats = await self.bot.corkus.guild.get(guild)
        results = await gather(*[self.fetch(member) for member in guild_stats.members])

        columns = {f'{guild} Members' : 36, 'Rank' : 26, 'Time Inactive' : 26}
        ascending_data = [result[1] for result in sorted(results, key = lambda item: item[0])]
        descending_data = [result[1] for result in sorted(results, key = lambda item: item[0], reverse=True)]
        ascending_table = table(columns, ascending_data, 5, 15, True, '(Ascending Order)')
        descending_table = table(columns, descending_data, 5, 15, True, '(Descending Order)')
        await paginator(self.bot, ctx, descending_table, message, ascending_table)

    async def fetch(self, member: Member):
        player = await member.fetch_player()

        if player.online:
            days_offline = 0
            display_time = 'Online'
        else:
            diff = datetime.now(timezone.utc) - player.last_online
            days_offline = diff.days + (diff.seconds / 86400)
            value = days_offline
            unit = 'day'
            if value < 1:
                value *= 24
                unit = 'hour'
                if value < 1:
                    value *= 60
                    unit = 'minute'
            if round(value) != 1:
                unit += 's'
            display_time = f'{round(value)} {unit}'
        return [days_offline, [member.username, member.rank.value.title(), display_time]]

def setup(bot: Pianobot):
    bot.add_cog(Inactivity(bot))
