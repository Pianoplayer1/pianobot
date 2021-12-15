from ..bot import Pianobot
from time import time

async def run(bot : Pianobot):
    db_terrs = dict(bot.query('SELECT name, guild FROM territories;'))
    notify = None
    missing = []
    territories = await bot.corkus.territory.list_all()

    for territory in territories:
        if territory.name not in db_terrs.keys():
            continue
        if db_terrs[territory.name] != territory.guild.name:  
            bot.query('UPDATE territories SET guild = %s WHERE name = %s;', (territory.guild.name, territory.name))
        if territory.guild.name != 'Eden':
            missing.append(territory)
            if db_terrs[territory.name] == 'Eden':
                notify = territory
    if notify is None: return

    terrs_msg = '\n'.join([f'- {terr.name} ({terr.guild.name})' for terr in missing][:10])
    if len(missing) > 10:
        terrs_msg += f'\n- ... ({len(missing) - 10} more)'
    msg = f'{notify.guild.name} has taken control of {notify.name}!```All missing territories ({len(missing)}):\n\n{terrs_msg}```'

    for channel, role, last_ping, cooldown in bot.query('SELECT `channel`, `role`, `time`, `ping` FROM `servers`;'):
        temp_msg = msg
        if role != 0 and cooldown != 0 and time() >= (last_ping + cooldown):
            temp_msg = f'<@&{role}>\n{msg}'
            bot.query('UPDATE `servers` SET `time` = %s WHERE `channel` = %s;', (time(), channel))
        try:
            await bot.get_channel(channel).send(temp_msg)
        except AttributeError:
            if channel != 0:
                print(f'Channel {channel} not found')
