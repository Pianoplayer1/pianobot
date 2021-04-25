from discord.ext import commands
from functions.permissions import permissions
import asyncio
from math import ceil

class Permissions(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(  name = 'permissions',
                        aliases = ['perms'],
                        brief = 'View perms.',
                        help = 'View permissions.',
                        hidden = True  )
    @commands.guild_only()
    async def permissions(self, ctx, channel = None, member = None, all_roles = None):
        try:
            channel = self.client.get_channel(int(channel))
        except TypeError:
            channel = ctx.channel
        guild = channel.guild
        try:
            member = guild.get_role(int(member)) or guild.get_member(int(member))
        except TypeError:
            member = ctx.author
        if all_roles:
            await ctx.send([chann.name for chann in guild.channels if 'view_channel' in permissions(self.client.user, chann, guild)])
            if id:
                for role in guild.roles:
                    perms = permissions(role, channel, guild)
                    if len(perms) > 0:
                        perms = '\n'.join(perms)
                        if role.name[0] == '>':
                            role.name = '\\' + role.name
                        await ctx.send(f'**{role.name}**:\n{perms}')
        else:
            await ctx.send('\n'.join(permissions(member, channel, guild)))
            await ctx.send(guid.roles)

def setup(client):
    client.add_cog(Permissions(client))
