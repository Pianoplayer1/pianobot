from discord.ext import commands
from functions.db import query
import re

class Role(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(name = 'role', brief = 'Sets the role to ping when Eden gets raided.', help = 'The role you set with this command will get pinged in a certain time interval in war situations. Enter the role by mentioning it as an argument.', usage = '<role>', hidden = True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def role(self, ctx, new):
        if re.search("^<@&[0-9]*>$", new):
            query("UPDATE servers SET role = %s WHERE id = %s;", (new[3:-1], ctx.guild.id))
            await ctx.send(f'Role changed to {new}')
        else:
            await ctx.send('Please enter a valid role (@...)!')

def setup(client):
    client.add_cog(Role(client))