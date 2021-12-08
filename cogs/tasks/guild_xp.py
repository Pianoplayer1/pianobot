import asyncio
from ..bot import Pianobot
from datetime import datetime, timedelta

async def run(bot : Pianobot) -> None:
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
        response = await response.json()
        current_xp = {member['name']: member['contributed'] for member in response['members']}
        columns = bot.query('SELECT "column_name" FROM "information_schema"."columns" WHERE "table_name" = \'guildXP\';')
        xp_values = bot.query('SELECT * FROM "guildXP" ORDER BY "time" DESC LIMIT 1;')
        last_xp = {columns[i][0]: xp_values[0][i] for i in range(1, len(columns))}
        
        to_add = set(current_xp.keys())
        to_add.difference_update(last_xp.keys())
        add_string = ', '.join([f'ADD COLUMN "{name}" VARCHAR NOT NULL' for name in to_add])
        to_remove = set(last_xp.keys())
        to_remove.difference_update(current_xp.keys())
        remove_string = ', '.join([f'DROP COLUMN IF EXISTS "{name}"' for name in to_remove])
        if add_string and remove_string:
            remove_string = ', ' + remove_string
        if add_string or remove_string:
            bot.query(f'ALTER TABLE "guildXP" {add_string}{remove_string};')

        time = datetime.utcnow()
        interval = 300
        seconds = (time.replace(tzinfo = None) - time.min).seconds
        difference = (seconds + interval / 2) // interval * interval - seconds
        rounded_time = str(time + timedelta(0, difference, -time.microsecond))

        columns = '", "'.join(current_xp.keys())
        placeholders = '%s' + ', %s' * len(current_xp)
        sql = f'INSERT INTO "guildXP"("time", "{columns}") VALUES ({placeholders});'
        values = (rounded_time, *current_xp.values())
        
        try:
            bot.query(sql, values)
        except:
            print('Duplicate guild xp time')