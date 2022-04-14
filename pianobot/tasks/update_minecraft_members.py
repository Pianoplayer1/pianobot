from asyncio import gather

from corkus.objects import Member

from pianobot import Pianobot
from pianobot.db.minecraft_members import MinecraftMember

async def update_minecraft_members(bot : Pianobot):
    db_members = [member.uuid for member in bot.database.minecraft_members.get_all()]
    eden = await bot.corkus.guild.get('Eden')
    await gather(*[process(member, bot, db_members) for member in eden.members])
    for uuid in set(db_members).difference({member.uuid.string() for member in eden.members}):
        bot.database.minecraft_members.remove(uuid)

async def process(member: Member, bot: Pianobot, db_members: list[MinecraftMember]):
    if member.uuid.string() not in db_members:
        bot.database.minecraft_members.add(
            member.uuid.string(),
            member.join_date
        )
    player = await member.fetch_player()
    bot.database.minecraft_members.update(
        member.uuid.string(),
        member.username,
        member.rank.name,
        player.last_online,
        player.online,
        member.contributed_xp
    )
