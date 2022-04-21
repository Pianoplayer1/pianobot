from discord import Role

from pianobot import Pianobot


async def add_discord_roles(bot: Pianobot) -> None:
    guild = bot.get_guild(682671629213368351)
    if guild is None:
        return
    db_roles = {role.discord_id: role for role in bot.database.discord_roles.get_all()}
    discord_roles: list[Role] = guild.roles

    for role in discord_roles:
        if (
            role.id not in db_roles
            or db_roles[role.id].name != role.name
            or db_roles[role.id].color != str(role.color)
            or db_roles[role.id].position != role.position
        ):
            bot.database.discord_roles.add_or_update(
                role.id, role.name, str(role.color), role.position
            )
