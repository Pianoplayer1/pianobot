from discord import GroupChannel, Object, User
from discord.ext.commands import Bot, Cog, Context, command, guild_only

from pianobot import Pianobot


class Sync(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @command(hidden=True)
    @guild_only()
    async def sync(self, ctx: Context[Bot], sync_globally: bool = False) -> None:
        if (
            isinstance(ctx.channel, GroupChannel)
            or isinstance(ctx.author, User)
            or ctx.guild is None
        ):
            return
        if ctx.channel.permissions_for(ctx.author).manage_guild:
            if sync_globally:
                await self.bot.tree.sync()
                await ctx.send('Slash commands have been synchronized globally')
            else:
                self.bot.tree.copy_global_to(guild=Object(ctx.guild.id))
                await self.bot.tree.sync(guild=Object(ctx.guild.id))
                await ctx.send('Slash commands have been synchronized on this server')

    @command(hidden=True)
    @guild_only()
    async def unsync(self, ctx: Context[Bot], unsync_globally: bool = False) -> None:
        if (
            isinstance(ctx.channel, GroupChannel)
            or isinstance(ctx.author, User)
            or ctx.guild is None
        ):
            return
        if ctx.channel.permissions_for(ctx.author).manage_guild:
            self.bot.tree.clear_commands(guild=None)
            if unsync_globally:
                await self.bot.tree.sync()
                await ctx.send('Slash commands have been removed globally')
            else:
                self.bot.tree.copy_global_to(guild=Object(ctx.guild.id))
                await self.bot.tree.sync(guild=Object(ctx.guild.id))
                await ctx.send('Slash commands have been removed from this server')


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(Sync(bot))
