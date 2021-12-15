from ..bot import Pianobot
from datetime import datetime, timedelta
import logging, math

async def run(bot : Pianobot) -> None:
    guild = await bot.corkus.guild.get('Eden')
    current_xp = {member.username: member.contributed_xp for member in guild.members}
    columns = [column[0] for column in bot.query('SELECT "column_name" FROM "information_schema"."columns" WHERE "table_name" = \'guildXP\';')[1:]]
    
    to_add = set(current_xp.keys())
    to_add.difference_update(columns)
    add_string = ', '.join([f'ADD COLUMN "{name}" BIGINT DEFAULT 0 NOT NULL' for name in to_add])
    to_remove = set(columns)
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
        logging.getLogger('tasks').debug('Duplicate guild xp time')
    
    data = bot.query('SELECT * FROM "guildXP" ORDER BY time DESC LIMIT 2;')
    members = [column[0] for column in bot.query('SELECT column_name FROM information_schema.columns WHERE table_name = \'guildXP\';')[1:]]
    xp_diff = [[members[i], data[0][i + 1] - data[1][i + 1]] for i in range(len(members)) if data[0][i + 1] - data[1][i + 1] > 0]
    if len(xp_diff) == 0: return

    msg = '--------------------------------------------------------------------------------'
    for pos, (name, xp) in enumerate(sorted(xp_diff, key = lambda item: item[1], reverse = True)):
        msg += f'\n**#{pos + 1} {name}** — `{format(xp)} XP | {format(xp / 5)} XP/min`'
    msg += f'\n**Total: ** `{format(sum([item[1] for item in xp_diff]))} XP`'
    channel = bot.get_channel(920757651380506644)
    if channel is not None:
        await channel.send(msg)

def format(n : float):
    names = ['',' Thousand',' Million',' Billion',' Trillion']
    if (n < 1000000): return n
    pos = max(0, min(len(names) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
    return f'{round(n / 10 ** (3 * pos), 2):g}{names[pos]}'