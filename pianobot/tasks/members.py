from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from corkus.errors import CorkusTimeoutError

if TYPE_CHECKING:
    from pianobot import Pianobot

LOGGER = getLogger('tasks.members')


async def members(bot: Pianobot) -> None:
    try:
        guild_members = (await bot.corkus.guild.get('Eden')).members
    except CorkusTimeoutError:
        LOGGER.warning('Error when fetching guild data of `Eden`')
        return

    database_members = await bot.database.members.get_all()
    saved_members: dict[str, tuple[str, str]] = {
        member.uuid.hex: (member.name, member.rank) for member in database_members
    }

    for corkus_member in guild_members:
        if corkus_member.uuid.hex in saved_members:
            saved_member = saved_members.pop(corkus_member.uuid.hex, None)
            if saved_member is None:
                LOGGER.info(
                    f'{corkus_member.username} has joined Eden as a {corkus_member.rank.name}!'
                )
                await bot.database.members.add(
                    corkus_member.uuid, corkus_member.username, corkus_member.rank.name
                )
            else:
                if corkus_member.username != saved_member[0]:
                    LOGGER.info(
                        f'{saved_member[0]} has changed their name to {corkus_member.username}!'
                    )
                    await bot.database.members.update_name(
                        corkus_member.uuid, corkus_member.username
                    )
                if corkus_member.rank.name != saved_member[1]:
                    LOGGER.info(
                        f'{corkus_member.username}: {saved_member[1]} -> {corkus_member.rank.name}'
                    )
                    await bot.database.members.update_rank(
                        corkus_member.uuid, corkus_member.rank.name
                    )

    for uuid, left_member in saved_members.items():
        LOGGER.info(f'{left_member[0]} ({left_member[1]}) has left Eden!')
        await bot.database.members.remove(
            next(m for m in database_members if m.uuid.hex == uuid).uuid
        )
