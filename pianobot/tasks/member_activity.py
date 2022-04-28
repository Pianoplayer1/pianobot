from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pianobot import Pianobot


async def member_activity(bot: Pianobot) -> None:
    guild = await bot.corkus.guild.get('Eden')
    player_list = await bot.corkus.network.online_players()
    online_members = [m.username for m in guild.members if player_list.is_player_online(m)]
    if len(online_members) > 0:
        await bot.database.member_activity.add(online_members)
