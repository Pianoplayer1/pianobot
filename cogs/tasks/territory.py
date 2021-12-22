from time import time

from ..bot import Pianobot

async def run(bot: Pianobot):
    db_terrs = {terr.name: terr for terr in bot.db.territories.get_all()}
    notify = None
    missing = []
    territories = await bot.corkus.territory.list_all()

    for territory in territories:
        if territory.name not in db_terrs.keys():
            continue
        if db_terrs[territory.name].guild != territory.guild.name:  
            bot.db.territories.update(territory.name, territory.guild.name)
        if territory.guild.name != 'Eden':
            missing.append(territory)
            if db_terrs[territory.name].guild == 'Eden':
                notify = territory
    if notify is None: return

    terrs_msg = '\n'.join([f'- {terr.name} ({terr.guild.name})' for terr in missing][:10])
    if len(missing) > 10:
        terrs_msg += f'\n- ... ({len(missing) - 10} more)'
    msg = f'{notify.guild.name} has taken control of {notify.name}!```All missing territories ({len(missing)}):\n\n{terrs_msg}```'

    for server in bot.db.servers.get_all():
        temp_msg = msg
        if server.role != 0 and server.ping != 0 and time() >= (server.time + server.ping):
            temp_msg = f'<@&{server.role}>\n{msg}'
            bot.db.servers.update_time(server.id, time())
        try:
            await bot.get_channel(server.channel).send(temp_msg)
        except AttributeError:
            if server.channel != 0:
                print(f'Channel {server.channel} not found')
