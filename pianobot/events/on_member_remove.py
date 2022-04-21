from discord import Member
from discord.ext.commands import Cog

from pianobot import Pianobot


class OnMemberRemove(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        self.bot.database.discord_members.update_and_remove(member)
        self.bot.database.discord_member_roles.remove_all(member.id)


def setup(bot: Pianobot) -> None:
    bot.add_cog(OnMemberRemove(bot))
