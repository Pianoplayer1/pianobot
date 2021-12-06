from time import time
from ..bot import Pianobot

async def run(bot : Pianobot):
    db_terrs = bot.query('SELECT `name`, `guild` FROM `territories`;')
    notify = None
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=territoryList') as response:
        terrs = (await response.json())['territories']

        for terr, guild in db_terrs:
            if terrs[terr]['guild'] != guild:  
                bot.query('UPDATE `territories` SET `guild` = %s WHERE `name` = %s;', (terrs[terr]['guild'], terr))
                print(f'{terr}: {guild} -> {terrs[terr]["guild"]}')
                if terrs[terr]['guild'] != 'Eden' and guild == 'Eden':
                    notify = terr

        if notify is None: return

        missing_terrs = [terr for entry in bot.query('SELECT `name` FROM `territories` WHERE `guild` != %s;', 'Eden') for terr in entry]
        terrs_msg = '\n'.join([f'- {terr} ({terrs[terr]["guild"]})' for terr in missing_terrs][:10])
        if len(missing_terrs) > 10:
            terrs_msg += f'\n- ... ({len(missing_terrs) - 10} more)'
        msg = f'{terrs[notify]["guild"]} has taken control of {notify}!```All missing territories ({len(missing_terrs)}):\n\n{terrs_msg}```'

        for channel, role, last_ping, cooldown in bot.query('SELECT `channel`, `role`, `time`, `ping` FROM `servers`;'):
            temp_msg = msg
            if role != 0 and cooldown != 0 and time() >= (last_ping + cooldown):
                temp_msg = f'<@&{role}>\n{msg}'
                bot.query('UPDATE `servers` SET `time` = %s WHERE `channel` = %s;', (time(), channel))
            try:
                await bot.get_channel(channel).send(temp_msg)
            except AttributeError:
                print(f'Channel {channel} not found')