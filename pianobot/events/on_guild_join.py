from discord import Guild
from discord.ext.commands import Cog

from pianobot import Pianobot

class OnGuildJoin(Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        print(f'Joined {guild.name}')
        self.bot.database.servers.add(guild.id)

def setup(bot: Pianobot):
    bot.add_cog(OnGuildJoin(bot))
