from discord.ext import commands
from functions.db import query

class Prefix(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(name = 'prefix', aliases = ['pre'], brief = 'Updates the bot prefix for this server.', help = 'Use this command to set a new bot prefix, which will be used to access this bot on this server. The prefix can consist of any letters, numbers and special characters, but make sure it does not conflict with another bot.', usage = '<new>', hidden = True)
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def prefix(self, ctx, new):
        query("UPDATE servers SET prefix = %s WHERE id = %s;", (new, ctx.guild.id))
        await ctx.send(f'Prefix changed to \'{new}\'')

def setup(client):
    client.add_cog(Prefix(client))