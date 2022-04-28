from __future__ import annotations

from asyncio import TimeoutError as AsyncioTimeoutError
from typing import TYPE_CHECKING

from discord import ButtonStyle, Interaction, InteractionMessage, Message, Reaction, User, ui
from discord.ext.commands import Context

from pianobot.utils.table import table

if TYPE_CHECKING:
    from pianobot import Pianobot


async def legacy_paginator(
    bot: Pianobot,
    ctx: Context,
    normal_contents: list[str],
    message: Message | None = None,
    reverse_contents: list[str] | None = None,
) -> None:
    contents = normal_contents
    page = 1

    if message is None:
        message = await ctx.send(contents[page - 1])
    else:
        await message.edit(content=contents[page - 1])

    if len(contents) == 1:
        return

    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    if reverse_contents is not None:
        await message.add_reaction('🔁')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(_reaction: Reaction, _user: User) -> bool:
        return (
            _user != bot.user
            and str(_reaction.emoji) in ['⏮', '◀', '🔁', '▶', '⏭']
            and _reaction.message.id == message.id
        )

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=300)
            await message.remove_reaction(reaction, user)

            if str(reaction.emoji) == '⏭' and page < len(contents):
                page = len(contents)
                await message.edit(content=f'{contents[page - 1]}')
            elif str(reaction.emoji) == '▶' and page != len(contents):
                page += 1
                await message.edit(content=f'{contents[page - 1]}')
            elif str(reaction.emoji) == '🔁' and reverse_contents is not None:
                if contents == normal_contents:
                    contents = reverse_contents
                else:
                    contents = normal_contents
                await message.edit(content=f'{contents[page - 1]}')
            elif str(reaction.emoji) == '◀' and page > 1:
                page -= 1
                await message.edit(content=f'{contents[page - 1]}')
            elif str(reaction.emoji) == '⏮' and page > 1:
                page = 1
                await message.edit(content=f'{contents[page - 1]}')

        except AsyncioTimeoutError:
            await message.remove_reaction('⏭', bot.user)
            await message.remove_reaction('▶', bot.user)
            if reverse_contents is not None:
                await message.remove_reaction('🔁', bot.user)
            await message.remove_reaction('◀', bot.user)
            await message.remove_reaction('⏮', bot.user)
            await message.edit(content=f'{contents[page - 1][:-3] + " (locked)```"}')
            break


class Buttons(ui.View):
    def __init__(self, normal_pages: list[str], reversed_pages: list[str] | None = None) -> None:
        super().__init__(timeout=300)
        self.current_page = 0
        self.current_pages = normal_pages
        self.normal_pages = normal_pages
        self.reversed_pages = reversed_pages
        self.max_page = len(self.normal_pages) - 1
        self.message: InteractionMessage = None
        if reversed_pages is None:
            self.remove_item(self.revert)

    async def handle_click(self, interaction: Interaction):
        self.current_page = min(max(self.current_page, 0), self.max_page)
        self.first_page.disabled = self.current_page == 0
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == self.max_page
        self.last_page.disabled = self.current_page == self.max_page
        await interaction.response.edit_message(
            content=self.current_pages[self.current_page],
            view=self,
        )

    async def on_timeout(self) -> None:
        content = (
            self.message.content[:-3] + ' (Locked)```'
            if self.reversed_pages is None
            else self.message.content[:-4] + ' - Locked)```'
        )
        await self.message.edit(content=content, view=None)

    @ui.button(disabled=True, emoji='⏮', style=ButtonStyle.gray)
    async def first_page(self, interaction: Interaction, _: ui.Button) -> None:
        self.current_page = 0
        await self.handle_click(interaction)

    @ui.button(disabled=True, emoji='◀', style=ButtonStyle.gray)
    async def previous_page(self, interaction: Interaction, _: ui.Button) -> None:
        self.current_page -= 1
        await self.handle_click(interaction)

    @ui.button(emoji='🔁', style=ButtonStyle.gray)
    async def revert(self, interaction: Interaction, _: ui.Button) -> None:
        self.current_pages = (
            self.reversed_pages if self.current_pages == self.normal_pages else self.normal_pages
        )
        await self.handle_click(interaction)

    @ui.button(emoji='▶', style=ButtonStyle.gray)
    async def next_page(self, interaction: Interaction, _: ui.Button) -> None:
        self.current_page += 1
        await self.handle_click(interaction)

    @ui.button(emoji='⏭', style=ButtonStyle.gray)
    async def last_page(self, interaction: Interaction, _: ui.Button) -> None:
        self.current_page = len(self.normal_pages) - 1
        await self.handle_click(interaction)


async def paginator(
    interaction: Interaction,
    data: list[list[str]],
    columns: dict[str, int],
    *,
    add_reverted_contents=False,
    rows_per_page: int = 15,
    separator_frequency: int = 5,
    enum: bool = True,
) -> None:
    if add_reverted_contents:
        ascending_data = table(
            columns, data, separator_frequency, rows_per_page, enum, '(Ascending Order)'
        )
        data.reverse()
        descending_data = table(
            columns, data, separator_frequency, rows_per_page, enum, '(Descending Order)'
        )
        initial_data = descending_data
        view = Buttons(descending_data, ascending_data) if len(descending_data) > 1 else None
    else:
        initial_data = table(columns, data, separator_frequency, rows_per_page, enum)
        view = Buttons(initial_data) if len(initial_data) > 1 else None

    if interaction.response.is_done():
        await (await interaction.original_message()).edit(content=initial_data[0], view=view)
    else:
        if view is None:
            await interaction.response.send_message(initial_data[0])
        else:
            await interaction.response.send_message(initial_data[0], view=view)
    if view is not None:
        view.message = await interaction.original_message()
