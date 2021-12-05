from discord.ext import commands
from ..utils.db import query
from ..utils.permissions import check_permissions
import discord

class Role(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(name = 'role', brief = 'Sets the role to ping when Eden gets raided.', help = 'The role you set with this command will get pinged in a certain time interval in war situations. Enter the role by mentioning it as an argument.', usage = '<role>', hidden = True)
    @commands.guild_only()
    async def role(self, ctx, new : discord.Role):
        if not check_permissions(ctx.author, ctx.channel, ['manage_roles']):
            await ctx.send('You don\'t have the required permissions to perform this action!')
            return
        query("UPDATE servers SET role = %s WHERE id = %s;", (new.id, ctx.guild.id))
        await ctx.send(f'Role changed to {new.mention}')

def setup(client):
    client.add_cog(Role(client))