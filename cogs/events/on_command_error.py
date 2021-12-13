from ..bot import Pianobot
from discord.ext import commands
import discord, sys, traceback

class OnCommandError(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx : commands.Context, error):
        if hasattr(ctx.command, 'on_error'):
            return
        cog = ctx.cog
        if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
            return
        if ctx.guild:
            prefix = self.bot.query('SELECT * FROM servers WHERE id = %s;', ctx.guild.id)
            prefix = prefix[0][1]
        else:
            prefix = '-'

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'You are missing the required `{error.param.name}` argument after this command. Refer to `{prefix}help {ctx.command}` for detailed information.')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'`{prefix}{ctx.command}` cannot be used in private messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.MissingPermissions):
            if ctx.guild:
                perms = ''.join(f'\n- `{perm}`' for perm in error.missing_perms)
                await ctx.send(f'You do not have the required permissions to run this command!\nFollowing permissions are needed:\n{perms}')
            else:
                await ctx.send(f'`{prefix}{ctx.command}` cannot be used in private messages.')
        elif isinstance(error, commands.CommandNotFound):
            pass
        else: 
            print(f'Ignoring exception in command {ctx.command}:', file = sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file = sys.stderr)

def setup(bot : Pianobot):
    bot.add_cog(OnCommandError(bot))