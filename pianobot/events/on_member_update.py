from discord import Member
from discord.ext.commands import Cog

from pianobot import Pianobot


class OnMemberUpdate(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if before.roles == after.roles:
            return

        for role in set(before.roles).difference(set(after.roles)):
            self.bot.database.discord_member_roles.remove(after.id, role.id)
        for role in set(after.roles).difference(set(before.roles)):
            self.bot.database.discord_member_roles.add(after.id, role.id)


def setup(bot: Pianobot) -> None:
    bot.add_cog(OnMemberUpdate(bot))
