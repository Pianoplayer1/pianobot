from discord.ext import commands

from pianobot import Pianobot


class Sync(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(hidden=True)
    @commands.guild_only()
    async def sync(self, ctx: commands.Context, sync_globally: bool = False) -> None:
        if ctx.channel.permissions_for(ctx.author).manage_guild:
            if sync_globally:
                await self.bot.tree.sync()
                await ctx.send('Slash commands have been synchronized globally')
            else:
                self.bot.tree.copy_global_to(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                await ctx.send('Slash commands have been synchronized on this server')

    @commands.command(hidden=True)
    @commands.guild_only()
    async def unsync(self, ctx: commands.Context, unsync_globally: bool = False) -> None:
        if ctx.channel.permissions_for(ctx.author).manage_guild:
            self.bot.tree.clear_commands(guild=None)
            if unsync_globally:
                await self.bot.tree.sync()
                await ctx.send('Slash commands have been removed globally')
            else:
                self.bot.tree.copy_global_to(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                await ctx.send('Slash commands have been removed from this server')


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(Sync(bot))
