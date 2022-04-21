from discord import Guild
from discord.ext.commands import Cog

from pianobot import Pianobot


class OnGuildRemove(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        self.bot.logger.info(f'Left {guild.name}')
        self.bot.database.servers.remove(guild.id)


def setup(bot: Pianobot) -> None:
    bot.add_cog(OnGuildRemove(bot))
