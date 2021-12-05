import time
from ..bot import Pianobot

async def run(bot : Pianobot):
    servers = bot.query("SELECT * FROM servers")
    db_terrs = dict(bot.query("SELECT * FROM territories"))
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=territoryList') as response:
        terrs = await response.json()
        terrs = terrs['territories']

        for terr in list(db_terrs.keys()):
            if terrs[terr]['guild'] != 'Eden' and db_terrs[terr] == 'Eden':
                ping_terr = terr
            if db_terrs[terr] != terrs[terr]['guild']:  
                bot.query("UPDATE territories SET guild = %s WHERE name = %s", (terrs[terr]['guild'], terr))
                print(f'{terr}: {db_terrs[terr]} -> {terrs[terr]["guild"]}')

        if 'ping_terr' in locals():
            tmissing = bot.query("SELECT name FROM territories WHERE guild != 'Eden'")
            msg = f'{terrs[ping_terr]["guild"]} has taken control of {ping_terr}!```All missing territories ({len(tmissing)}):\n'
            for terr in tmissing:
                terr = terr[0]
                msg += f'\n- {terr} ({terrs[terr]["guild"]})'
            msg += '```'

            for server in servers:
                msgTemp = msg
                if server[3] != 0 and time.time() >= (server[4] + server[5]) and server[5] != 0:
                    msgTemp = f'<@&{server[3]}>\n' + msg
                    bot.query("UPDATE servers SET time = %s WHERE id = %s", (time.time(), server[0]))
                try:
                    await bot.get_channel(server[2]).send(msgTemp)
                except:
                    print(f'Couldn\'t send message to server {server[0]}')