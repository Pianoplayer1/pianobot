from logging import getLogger
from time import time

from discord import TextChannel
from discord.errors import Forbidden

from pianobot import Pianobot


async def territories(bot: Pianobot) -> None:
    db_terrs = {terr.name: terr for terr in bot.database.territories.get_all()}
    notify = None
    missing = []
    wynn_territories = await bot.corkus.territory.list_all()

    for territory in wynn_territories:
        guild_name = None if territory.guild is None else territory.guild.name
        if territory.name not in db_terrs.keys():
            continue
        if db_terrs[territory.name].guild != guild_name:
            bot.database.territories.update(territory.name, guild_name)
        if guild_name != 'Eden':
            missing.append(territory)
            if db_terrs[territory.name].guild == 'Eden' and territory.guild is not None:
                notify = territory
    if len(missing) == 0 and any(terr.guild != 'Eden' for terr in db_terrs.values()):
        for server in bot.database.servers.get_all():
            try:
                channel = bot.get_channel(server.channel)
                if channel is None or not isinstance(channel, TextChannel):
                    raise AttributeError
                await channel.send('Fully reclaimed!')
            except (AttributeError, Forbidden):
                if server.channel != 0:
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

    for server in bot.database.servers.get_all():
        temp_msg = msg
        if (
            server.role != 0
            and server.ping != 0
            and time() >= (server.time + server.ping)
            and (6 if server.rank == -1 else server.rank) > highest_rank
        ):
            temp_msg = f'<@&{server.role}>\n{msg}'
            bot.database.servers.update_time(server.server_id, time())
        try:
            channel = bot.get_channel(server.channel)
            if channel is None or not isinstance(channel, TextChannel):
                raise AttributeError
            await channel.send(temp_msg)
        except (AttributeError, Forbidden):
            if server.channel != 0:
                getLogger('tasks.territories').warning('Channel %s not found', server.channel)
