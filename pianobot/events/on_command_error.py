from sys import stderr
from traceback import print_exception

from discord import HTTPException
from discord.ext import commands

from pianobot import Pianobot

class OnCommandError(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if hasattr(ctx.command, 'on_error'):
            return
        cog: commands.Cog = ctx.cog
        if cog and getattr(
            cog.cog_command_error.__func__,
            '__cog_special_method__',
            cog.cog_command_error
        ) is not None:
            return
        prefix = '-'
        if ctx.guild:
            server = self.bot.database.servers.get(ctx.guild.id)
            if server:
                prefix = server.prefix

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'You are missing the required `{error.param.name}` argument after this command.'
                f' Refer to `{prefix}help {ctx.command}` for detailed information.'
            )
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'`{ctx.command}` cannot be used in private messages.')
            except HTTPException:
                pass
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(
                f'One of your command arguments has the wrong type.'
                f' Refer to `{prefix}help {ctx.command}` for detailed information.'
            )
        elif isinstance(error, commands.MissingPermissions):
            if ctx.guild:
                perms = ''.join(f'\n- `{perm}`' for perm in error.missing_perms)
                await ctx.send(
                    'You do not have the required permissions to run this command!\n'
                    f'Following permissions are needed:\n{perms}'
                )
            else:
                await ctx.send(f'`{prefix}{ctx.command}` cannot be used in private messages.')
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(f'Ignoring exception in command {ctx.command}:', file = stderr)
            print_exception(type(error), error, error.__traceback__, file = stderr)

def setup(bot: Pianobot):
    bot.add_cog(OnCommandError(bot))
