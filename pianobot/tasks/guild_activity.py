from __future__ import annotations

from asyncio import gather
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pianobot import Pianobot


async def guild_activity(bot: Pianobot) -> None:
    guilds: dict[str, int | None] = dict()

    for name, online_members in await gather(*[fetch(bot, guild) for guild in bot.tracked_guilds]):
        guilds[name] = online_members

    await bot.database.guild_activity.add(guilds)


async def fetch(bot: Pianobot, name: str) -> tuple[str, int | None]:
    response = await bot.session.get(f'https://web-api.wynncraft.com/api/v3/guild/{name}')
    guild = await response.json()
    if response.status != 200:
        getLogger('tasks.guild_activity').warning(
            'Error when fetching guild data of `%s`: %s', name, guild
        )
        return name, None
    return name, guild['onlineMembers']
