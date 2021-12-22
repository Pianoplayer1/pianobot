from discord import Guild
from discord.ext.commands import Cog

from ..bot import Pianobot

class OnGuildRemove(Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        print(f'Left {guild.name}')
        self.bot.db.servers.remove(guild.id)

def setup(bot: Pianobot):
    bot.add_cog(OnGuildRemove(bot))
