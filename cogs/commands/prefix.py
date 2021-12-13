from ..bot import Pianobot
from discord.ext import commands
from ..utils.permissions import check_permissions

class Prefix(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot
    
    @commands.command(  name = 'prefix',
                        aliases = ['pre'],
                        brief = 'Updates the bot prefix for this server.',
                        help = 'Use this command to set a new bot prefix, which will be used to access this bot on this server. The prefix can consist of any letters, numbers and special characters, but make sure it does not conflict with another bot.',
                        usage = '<new>',
                        hidden = True)
    @commands.guild_only()
    async def prefix(self, ctx : commands.Context, new : str):
        if len(new) > 3:
            await ctx.send('A prefix cannot be longer than 3 characters!')
            return
        if not check_permissions(ctx.author, ctx.channel, 'manage_guild'):
            await ctx.send('You don\'t have the required permissions to perform this action!')
            return
        self.bot.query('UPDATE servers SET prefix = %s WHERE id = %s;', (new, ctx.guild.id))
        await ctx.send(f'Prefix changed to \'{new}\'')

def setup(bot : Pianobot):
    bot.add_cog(Prefix(bot))