from discord import Member

from pianobot import Pianobot

async def add_discord_member_roles(bot : Pianobot):
    discord_members: list[Member] = bot.get_guild(682671629213368351).members
    for member in discord_members:
        roles: list[int] = [role.id for role in member.roles]
        db_roles = [entry.role_id for entry in bot.database.discord_member_roles.get_all(member.id)]

        for role in set(db_roles).difference(set(roles)):
            bot.database.discord_member_roles.remove(member.id, role)
        for role in set(roles).difference(set(db_roles)):
            bot.database.discord_member_roles.add(member.id, role)
