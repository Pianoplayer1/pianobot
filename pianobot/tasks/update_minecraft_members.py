from asyncio import gather

from corkus.objects import Member

from pianobot import Pianobot
from pianobot.db.minecraft_members import MinecraftMember

async def update_minecraft_members(bot : Pianobot):
    db_members = {member.uuid: member for member in bot.database.minecraft_members.get_all()}
    eden = await bot.corkus.guild.get('Eden')
    await gather(*[process(member, bot, db_members) for member in eden.members])
    for uuid in set(db_members).difference({member.uuid.string() for member in eden.members}):
        bot.database.minecraft_members.remove(uuid)

async def process(member: Member, bot: Pianobot, db_members: dict[str, MinecraftMember]):
    uuid = member.uuid.string()
    player = await member.fetch_player()
    if uuid not in db_members:
        bot.database.minecraft_members.add(
            uuid,
            member.username,
            member.rank.name.capitalize(),
            member.join_date,
            player.last_online,
            player.online,
            member.contributed_xp
        )
    elif (
        member.username != db_members[uuid].name
        or member.rank.name.capitalize() != db_members[uuid].rank
        or player.last_online != db_members[uuid].last_seen
        or player.online != db_members[uuid].online
        or member.contributed_xp != db_members[uuid].gxp
    ):
        bot.database.minecraft_members.update(
            uuid,
            member.username,
            member.rank.name.capitalize(),
            player.last_online,
            player.online,
            member.contributed_xp
        )
