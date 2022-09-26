from __future__ import annotations

from logging import getLogger
from math import floor, log10
from os import getenv
from typing import TYPE_CHECKING

from corkus.errors import CorkusTimeoutError
from discord import TextChannel

if TYPE_CHECKING:
    from pianobot import Pianobot


async def guild_xp(bot: Pianobot) -> None:
    try:
        guild = await bot.corkus.guild.get('Eden')
    except CorkusTimeoutError:
        getLogger('tasks.guild_xp').warning('Error when fetching guild data of `Eden`')
        return
    current_xp = {member.username: member.contributed_xp for member in guild.members}

    await bot.database.guild_xp.update_columns(list(current_xp.keys()))
    await bot.database.guild_xp.add(current_xp)

    data = await bot.database.guild_xp.get_last(2)
    new = data[0]
    old = data[1]
    xp_diff = []
    for name, new_xp in new.data.items():
        old_xp = old.data.get(name, None)
        if new_xp is not None and old_xp is not None and new_xp - old_xp > 0:
            xp_diff.append((name, new_xp - old_xp))
    if len(xp_diff) == 0:
        return

    msg = '--------------------------------------------------------------------------------'
    for pos, (name, gxp) in enumerate(sorted(xp_diff, key=lambda item: item[1], reverse=True)):
        msg += f'\n**#{pos + 1} {name}** — `{format(gxp)} XP | {format(gxp / 5)} XP/min`'
    msg += f'\n**Total: ** `{display(sum([item[1] for item in xp_diff]))} XP`'

    channel = bot.get_channel(int(getenv('XP_CHANNEL', 0)))
    if isinstance(channel, TextChannel):
        await channel.send(msg)
    elif getenv('XP_CHANNEL') is not None:
        getLogger('tasks.guild_xp').warning('Channel %s not found', getenv('XP_CHANNEL'))


def display(num: float) -> str:
    names = ['', ' Thousand', ' Million', ' Billion', ' Trillion']
    if num < 10000:
        return str(num)
    pos = max(0, min(len(names) - 1, int(floor(0 if num == 0 else log10(abs(num)) / 3))))
    return f'{round(num / 10 ** (3 * pos), 2):g}{names[pos]}'
