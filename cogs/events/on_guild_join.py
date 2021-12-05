from ..bot import Pianobot
from discord.ext.commands import Cog
from discord import Guild

class OnGuildJoin(Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot
    
    @Cog.listener()
    async def on_guild_join(self, guild : Guild):
        print(f'Joined {guild.name}')
        self.bot.query("INSERT INTO `servers` (`id`) VALUES (%s);", guild.id)

def setup(bot : Pianobot):
    bot.add_cog(OnGuildJoin(bot))