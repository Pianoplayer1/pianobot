from asyncio import gather, sleep

from corkus.objects.member import Member
from discord import app_commands, Interaction, Message
from discord.ext import commands
from discord.ui import select, Select, View

from pianobot import Pianobot
from pianobot.utils import format_last_seen, legacy_paginator, paginator, table


class LegacyInactivity(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        aliases=['act', 'activity', 'inact'],
        brief='Outputs the member inactivity times of a specified guild.',
        help=(
            'This command returns a table with the times since each member of a specified guild'
            ' has been last seen on the Wynncraft server.'
        ),
        name='inactivity',
        usage='<guild>',
    )
    async def inactivity(self, ctx: commands.Context, *, guild: str) -> None:
        await ctx.send(
            '```prolog\nNote: this command has been updated with a slash command version:\n     '
            ' \'/inactivity <guild>\' is the new way to access inactivity tables.\n     '
            ' \'-inactivity <guild>\' (the command you just used) will only work for limited'
            ' time.```'
        )
        await ctx.trigger_typing()
        guilds = await self.bot.corkus.guild.list_all()
        guilds = [g.name for g in guilds]
        try:
            matches = [guilds[list(map(str.lower, guilds)).index(guild.lower())]]
        except ValueError:
            matches = [g for g in guilds if guild.lower() in g.lower()]
        if len(matches) == 0:
            await ctx.send(
                f'No guild names include \'{guild}\'. Please try again with a correct guild name.'
            )
            return
        if len(matches) == 1:
            guild = matches[0]
            message = None
        elif len(matches) <= 5:
            message = await ctx.send(
                f'Several guild names include `{guild}`.'
                ' Enter the number of one of the following guilds to view their inactivity.\n'
                ' To leave this prompt, type `exit`:\n\n'
                + '\n'.join([f'{match + 1}. {matches[match]}' for match in range(len(matches))])
            )

            def check(msg: Message) -> bool:
                return msg.author == ctx.author and msg.channel == ctx.channel

            answer_msg = await self.bot.wait_for('message', check=check)
            if ctx.channel.permissions_for(self.bot.user).manage_messages:
                await answer_msg.delete()

            try:
                guild = matches[int(answer_msg.content) - 1]
            except (IndexError, ValueError):
                if answer_msg.content == 'exit':
                    await message.edit(content='Prompt exited.')
                else:
                    await message.edit(content='Invalid input, exited prompt.')
                await sleep(6)
                await message.delete()
                return
        else:
            await ctx.send(
                f'Several guild names include \'{guild}\'.'
                ' Please try again with a more precise name.'
            )
            return

        guild_stats = await self.bot.corkus.guild.get(guild)
        results = await gather(*[fetch(member) for member in guild_stats.members])
        results = [result[1] for result in sorted(results, key=lambda item: item[0])]

        columns = {f'{guild} Members': 36, 'Rank': 26, 'Time Inactive': 26}
        ascending_table = table(columns, results, 5, 15, True, '(Ascending Order)')
        results.reverse()
        descending_table = table(columns, results, 5, 15, True, '(Descending Order)')
        await legacy_paginator(self.bot, ctx, descending_table, message, ascending_table)


class SelectMenu(View):
    def __init__(self, guilds: list[str], cog: 'Inactivity'):
        super().__init__()
        self.cog = cog
        for guild in sorted(guilds):
            self.select_menu.add_option(label=guild, value=guild)

    @select()
    async def select_menu(self, interaction: Interaction, menu: Select):
        menu.disabled = True
        menu.placeholder = menu.values[0]
        await interaction.response.edit_message(view=self)
        await self.cog.inactivity_for(menu.values[0], interaction)


class Inactivity(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @app_commands.command(description='Member activity table for a Wynncraft guild')
    async def inactivity(self, interaction: Interaction, guild: str) -> None:
        await interaction.response.defer()
        guilds = [g.name for g in await self.bot.corkus.guild.list_all()]
        if guild in guilds:
            await self.inactivity_for(guild, interaction)
            return

        full_matches = []
        partial_matches = []
        for guild_name in guilds:
            if guild.lower() == guild_name.lower():
                full_matches.append(guild_name)
            elif guild.lower() in guild_name.lower():
                partial_matches.append(guild_name)

        matches = full_matches or partial_matches
        if len(matches) == 0:
            await interaction.followup.send(
                f'No guild names include `{guild}`. Please try again with a correct guild name.'
            )
        elif len(matches) == 1:
            await self.inactivity_for(matches[0], interaction)
        elif len(matches) <= 5:
            await interaction.followup.send(
                f'Several guild names include `{guild}`, please select the one you meant:',
                view=SelectMenu(matches, self),
            )
        else:
            await interaction.followup.send(
                f'{len(matches)} guild names include `{guild}`. Please try again with a more'
                ' precise name.'
            )

    async def inactivity_for(self, guild: str, interaction: Interaction):
        guild_stats = await self.bot.corkus.guild.get(guild)
        results = await gather(*[fetch(member) for member in guild_stats.members])
        results = [result[1] for result in sorted(results, key=lambda item: item[0])]

        columns = {f'{guild} Members': 36, 'Rank': 26, 'Time Inactive': 26}
        await paginator(interaction, results, columns, add_reverted_contents=True)


async def fetch(member: Member) -> tuple[float, tuple[str, str, str]]:
    player = await member.fetch_player()
    raw_days, display_time = format_last_seen(player)

    return raw_days, (member.username, member.rank.value.title(), display_time)


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(LegacyInactivity(bot))
    await bot.add_cog(Inactivity(bot))
