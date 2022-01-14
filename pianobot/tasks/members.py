from datetime import datetime

from pianobot import Pianobot

async def members(bot : Pianobot):
    db_members = [member.name for member in bot.database.members.get_all()]
    eden = await bot.corkus.guild.get('Eden')
    for member in eden.members:
        if member.uuid.string() not in db_members:
            bot.database.members.add(
                member.uuid.string(),
                (member.join_date - datetime(1970, 1, 1)).total_seconds()
            )
        bot.database.members.update(
            member.username,
            member.rank.value,
            member.contributed_xp,
            member.uuid.string()
        )
