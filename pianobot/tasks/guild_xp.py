from __future__ import annotations

from math import floor, log10
from typing import TYPE_CHECKING

from discord import TextChannel

if TYPE_CHECKING:
    from pianobot import Pianobot


async def guild_xp(bot: Pianobot) -> None:
    guild = await bot.corkus.guild.get('Eden')
    current_xp = {member.username: member.contributed_xp for member in guild.members}

    await bot.database.guild_xp.update_columns(list(current_xp.keys()))
    await bot.database.guild_xp.add(current_xp)

    data = await bot.database.guild_xp.get_last(2)
    new = data[0]
    old = data[1]
    xp_diff = [
        (name, xp - old.data.get(name, 0))
        for name, xp in new.data.items()
        if xp - old.data.get(name, 0) > 0
    ]
    if len(xp_diff) == 0:
        return

    msg = '--------------------------------------------------------------------------------'
    for pos, (name, gxp) in enumerate(sorted(xp_diff, key=lambda item: item[1], reverse=True)):
        msg += f'\n**#{pos + 1} {name}** — `{format(gxp)} XP | {format(gxp / 5)} XP/min`'
    msg += f'\n**Total: ** `{display(sum([item[1] for item in xp_diff]))} XP`'
    channel = await bot.fetch_channel(920757651380506644)
    if channel is not None and isinstance(channel, TextChannel):
        await channel.send(msg)

    await bot.database.guild_xp.cleanup()


def display(num: float) -> str:
    names = ['', ' Thousand', ' Million', ' Billion', ' Trillion']
    if num < 10000:
        return str(num)
    pos = max(0, min(len(names) - 1, int(floor(0 if num == 0 else log10(abs(num)) / 3))))
    return f'{round(num / 10 ** (3 * pos), 2):g}{names[pos]}'
