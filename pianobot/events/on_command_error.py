from logging import getLogger
from traceback import TracebackException

from discord import HTTPException
from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import get_prefix


class OnCommandError(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if hasattr(ctx.command, 'on_error'):
            return
        prefix = await get_prefix(self.bot.database.servers, ctx.guild)

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
                f'One of your command arguments is wrong. Refer to `{prefix}help {ctx.command}`'
                ' for detailed information.'
            )
        elif isinstance(error, commands.MissingPermissions):
            if ctx.guild:
                perms = ''.join(f'\n- `{perm}`' for perm in error.missing_permissions)
                await ctx.send(
                    'You do not have the required permissions to run this command!\nFollowing'
                    f' permissions are needed:\n{perms}'
                )
            else:
                await ctx.send(f'`{prefix}{ctx.command}` cannot be used in private messages.')
        elif isinstance(error, commands.CommandNotFound):
            if ctx.prefix.startswith('<@'):
                await ctx.send(f'Use `{prefix}help` for a list of things I can do.')
            self.bot.logger.info(error.args[0])
        else:
            getLogger('commands').warning(
                'Ignoring exception in command %s:\n%s',
                ctx.command,
                "".join(
                    TracebackException(
                        type(error), error, error.__traceback__, compact=True
                    ).format()
                ),
            )


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(OnCommandError(bot))
