from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import check_permissions

class Prefix(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(
        aliases = ['pre'],
        brief = 'Updates the bot prefix for this server.',
        description = 'guild_only',
        help = 'Use this command to set a new bot prefix, which will be used to access this bot on'
            ' this server. The prefix can consist of any letters, numbers and special characters,'
            ' but make sure it does not conflict with another bot.',
        name = 'prefix',
        usage = '<new>'
    )
    @commands.guild_only()
    async def prefix(self, ctx: commands.Context, new: str):
        if len(new) > 3:
            await ctx.send('A prefix cannot be longer than 3 characters!')
            return
        if not check_permissions(ctx.author, ctx.channel, 'manage_guild'):
            await ctx.send('You don\'t have the required permissions to perform this action!')
            return
        self.bot.database.servers.update_prefix(ctx.guild.id, new)
        await ctx.send(f'Prefix changed to \'{new}\'')

def setup(bot: Pianobot):
    bot.add_cog(Prefix(bot))