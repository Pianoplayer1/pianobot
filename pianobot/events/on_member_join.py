from discord import Member
from discord.ext.commands import Cog

from pianobot import Pianobot

class OnMemberJoin(Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member: Member):
        self.bot.database.discord_members.add_or_update(
            member.id,
            member.nick or member.name,
            member.avatar_url
        )

def setup(bot: Pianobot):
    bot.add_cog(OnMemberJoin(bot))
