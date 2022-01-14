from time import time

from discord.errors import Forbidden

from pianobot import Pianobot

async def territories(bot: Pianobot):
    db_terrs = {terr.name: terr for terr in bot.database.territories.get_all()}
    notify = None
    missing = []
    wynn_territories = await bot.corkus.territory.list_all()

    for territory in wynn_territories:
        if territory.name not in db_terrs.keys():
            continue
        if db_terrs[territory.name].guild != territory.guild.name:
            bot.database.territories.update(territory.name, territory.guild.name)
        if territory.guild.name != 'Eden':
            missing.append(territory)
            if db_terrs[territory.name].guild == 'Eden':
                notify = territory
    if len(missing) == 0 and any(terr.guild != 'Eden' for terr in db_terrs.values()):
        for server in bot.database.servers.get_all():
            try:
                await bot.get_channel(server.channel).send('Fully reclaimed!')
            except (AttributeError, Forbidden):
                if server.channel != 0:
                    print(f'Channel {server.channel} not found')
    if notify is None:
        return

    terrs_msg = '\n'.join([f'- {terr.name} ({terr.guild.name})' for terr in missing][:10])
    if len(missing) > 10:
        terrs_msg += f'\n- ... ({len(missing) - 10} more)'
    msg = (
        f'{notify.guild.name} has taken control of {notify.name}!'
        f'```All missing territories ({len(missing)}):\n\n{terrs_msg}```'
    )

    for server in bot.database.servers.get_all():
        temp_msg = msg
        if server.role != 0 and server.ping != 0 and time() >= (server.time + server.ping):
            temp_msg = f'<@&{server.role}>\n{msg}'
            bot.database.servers.update_time(server.id, time())
        try:
            await bot.get_channel(server.channel).send(temp_msg)
        except (AttributeError, Forbidden):
            if server.channel != 0:
                print(f'Channel {server.channel} not found')
