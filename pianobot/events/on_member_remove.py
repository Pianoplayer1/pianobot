from discord import Member
from discord.ext.commands import Cog

from pianobot import Pianobot

class OnMemberRemove(Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        self.bot.database.discord_members.update_and_remove(
            member.id,
            member.nick or member.name,
            member.avatar_url
        )

def setup(bot: Pianobot):
    bot.add_cog(OnMemberRemove(bot))
