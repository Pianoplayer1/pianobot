from discord.ext import commands
from functions.db import query
import discord, sys, traceback

class On_command_error(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        cog = ctx.cog
        if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
            return
        if ctx.guild:
            prefix = query('SELECT * FROM servers WHERE id = %s', ctx.guild.id)
            prefix = prefix[0][1]
        else:
            prefix = '-'
        if isinstance(error, commands.CommandNotFound):
            try:
                #await ctx.send(f'I don\'t know this command. Use `{prefix}help` to get a list of things I can do.')
                pass
            except discord.Forbidden:
                print(f'\'{ctx.message.content}\' could not be processed in #{ctx.channel.name} in {ctx.guild.name}')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'You are missing the required \'{error.param}\' argument after this command. Refer to `{prefix}help {ctx.command}` for detailed information.')
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
        else: 
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(client):
    client.add_cog(On_command_error(client))
