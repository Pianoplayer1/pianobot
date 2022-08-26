from __future__ import annotations

from logging import getLogger
from time import time
from typing import TYPE_CHECKING

from corkus.errors import CorkusTimeoutError
from discord import TextChannel

if TYPE_CHECKING:
    from pianobot import Pianobot


async def territories(bot: Pianobot) -> None:
    db_terrs = {terr.name: terr for terr in await bot.database.territories.get_all()}
    notify = None
    missing = []
    try:
        wynn_territories = await bot.corkus.territory.list_all()
    except CorkusTimeoutError:
        getLogger('tasks.territories').warning('Error when fetching list of territories')
        return

    for territory in wynn_territories:
        guild_name = None if territory.guild is None else territory.guild.name
        if territory.name not in db_terrs.keys():
            continue
        if db_terrs[territory.name].guild != guild_name:
            await bot.database.territories.update(territory.name, guild_name)
        if guild_name != 'Eden':
            missing.append(territory)
            if db_terrs[territory.name].guild == 'Eden' and territory.guild is not None:
                notify = territory
    if len(missing) == 0 and any(terr.guild != 'Eden' for terr in db_terrs.values()):
        for server in await bot.database.servers.get_all():
            channel = bot.get_channel(server.channel)
            if isinstance(channel, TextChannel):
                await channel.send('Fully reclaimed!')
            elif server.channel != 0:
                getLogger('tasks.territories').warning('Channel %s not found', server.channel)
    if notify is None:
        return

    terrs_msg = '\n'.join([f'- {terr.name} ({terr.guild.name})' for terr in missing][:10])
    if len(missing) > 10:
        terrs_msg += f'\n- ... ({len(missing) - 10} more)'
    msg = (
        f'{notify.guild.name if notify.guild is not None else None} has taken control of'
        f' {notify.name}!```All missing territories ({len(missing)}):\n\n{terrs_msg}```'
    )

    eden = await bot.corkus.guild.get('Eden')
    player_list = await bot.corkus.network.online_players()
    highest_rank = max(
        (int(member.rank) for member in eden.members if player_list.is_player_online(member)),
        default=-1,
    )

    for server in await bot.database.servers.get_all():
        temp_msg = msg
        if (
            server.role != 0
            and server.ping != 0
            and time() >= (server.time + server.ping)
            and (6 if server.rank == -1 else server.rank) > highest_rank
        ):
            temp_msg = f'<@&{server.role}>\n{msg}'
            await bot.database.servers.update_time(server.server_id, time())
        channel = bot.get_channel(server.channel)
        if isinstance(channel, TextChannel):
            await channel.send(temp_msg)
        elif server.channel != 0:
            getLogger('tasks.territories').warning('Channel %s not found', server.channel)
