from datetime import datetime

from pianobot import Pianobot

async def members(bot : Pianobot):
    db_members = dict(bot.database._con.query('SELECT uuid, name FROM members;'))
    eden = await bot.corkus.guild.get('Eden')
    for member in eden.members:
        if member.uuid.string() not in db_members:
            epoch = (member.join_date - datetime(1970, 1, 1)).total_seconds()
            bot.database._con.query(
                'INSERT INTO members(uuid, joined) VALUES (%s, %s)',
                member.uuid.string(), epoch
            )
        bot.database._con.query(
            'UPDATE members SET name=%s, rank=%s, xp=%s WHERE uuid=%s',
            member.username,
            member.rank.value.capitalize(),
            member.contributed_xp,
            member.uuid.string()
        )
