from __future__ import annotations

from asyncio import TimeoutError as AsyncioTimeoutError
from typing import TYPE_CHECKING

from discord import Message, Reaction, User
from discord.ext.commands import Context

if TYPE_CHECKING:
    from pianobot import Pianobot


async def paginator(
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

    await message.add_reaction('⏮️')
    await message.add_reaction('◀️')
    if reverse_contents is not None:
        await message.add_reaction('🔁')
    await message.add_reaction('▶️')
    await message.add_reaction('⏭️')

    def check(_reaction: Reaction, _user: User) -> bool:
        return (
            _user != bot.user
            and str(_reaction.emoji) in ['⏮️', '◀️', '🔁', '▶️', '⏭️']
            and _reaction.message == message
        )

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=300)
            await message.remove_reaction(reaction, user)

            if str(reaction.emoji) == '⏭️' and page < len(contents):
                page = len(contents)
                await message.edit(content=f'{contents[page-1]}')
            elif str(reaction.emoji) == '▶️' and page != len(contents):
                page += 1
                await message.edit(content=f'{contents[page-1]}')
            elif str(reaction.emoji) == '🔁' and reverse_contents is not None:
                if contents == normal_contents:
                    contents = reverse_contents
                else:
                    contents = normal_contents
                await message.edit(content=f'{contents[page-1]}')
            elif str(reaction.emoji) == '◀️' and page > 1:
                page -= 1
                await message.edit(content=f'{contents[page-1]}')
            elif str(reaction.emoji) == '⏮️' and page > 1:
                page = 1
                await message.edit(content=f'{contents[page-1]}')

        except AsyncioTimeoutError:
            await message.remove_reaction('⏭️', bot.user)
            await message.remove_reaction('▶️', bot.user)
            if reverse_contents is not None:
                await message.remove_reaction('🔁', bot.user)
            await message.remove_reaction('◀️', bot.user)
            await message.remove_reaction('⏮️', bot.user)
            await message.edit(content=f'{contents[page - 1][:-3] + " (locked)```"}')
            break
