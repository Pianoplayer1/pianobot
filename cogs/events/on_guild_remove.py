from ..bot import Pianobot
from discord.ext.commands import Cog
from discord import Guild

class OnGuildRemove(Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot
    
    @Cog.listener()
    async def on_guild_remove(self, guild : Guild):
        print(f'Left {guild.name}')
        self.bot.query("DELETE FROM `servers` WHERE `id` = %s;", guild.id)

def setup(bot : Pianobot):
    bot.add_cog(OnGuildRemove(bot))