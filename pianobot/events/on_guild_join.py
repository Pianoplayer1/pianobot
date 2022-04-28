from discord import Guild
from discord.ext.commands import Cog

from pianobot import Pianobot


class OnGuildJoin(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        self.bot.logger.info(f'Joined {guild.name}')
        await self.bot.database.servers.add(guild.id)


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(OnGuildJoin(bot))
