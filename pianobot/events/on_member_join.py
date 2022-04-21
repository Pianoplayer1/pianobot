from discord import Member
from discord.ext.commands import Cog

from pianobot import Pianobot


class OnMemberJoin(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        self.bot.database.discord_members.add_or_update(member)


def setup(bot: Pianobot) -> None:
    bot.add_cog(OnMemberJoin(bot))
