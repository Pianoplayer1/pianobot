from discord import Member

from pianobot import Pianobot

async def add_discord_members(bot : Pianobot):
    db_members = {member.discord_id: member for member in bot.database.discord_members.get_all()}
    discord_members: list[Member] = bot.get_guild(682671629213368351).members

    for member in discord_members:
        if (
            member.id not in db_members
            or db_members[member.id].nickname != (member.nick or member.name)
            or db_members[member.id].username != member.name
            or db_members[member.id].tag != member.tag
            or db_members[member.id].avatar_url != str(member.avatar_url)
        ):
            bot.database.discord_members.add_or_update(
                member.id,
                member.nick or member.name,
                member.name,
                member.tag,
                str(member.avatar_url)
            )
