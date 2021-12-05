import discord
import typing
from discord.ext import commands
from ..utils.permissions import permissions

class Permissions(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(  name = 'permissions',
                        aliases = ['perms'],
                        brief = 'View perms.',
                        help = 'View permissions.',
                        hidden = True  )
    @commands.guild_only()
    async def permissions(self, ctx, target : typing.Union[discord.Member, discord.Role] = None, channel : typing.Union[discord.TextChannel, discord.VoiceChannel] = None, *, args = ''):
        if channel is None:
            channel = ctx.channel
        if target is None:
            target = ctx.author
        
        if 'all' in args:
            for role in channel.guild.roles:
                perms = permissions(role, channel)
                if len(perms) > 0:
                    perms = '\n'.join(perms)
                    if role.name[0] == '>':
                        role.name = '\\' + role.name
                    await ctx.send(f'**{role.name}**:\n{perms}')
        else:
            perms = permissions(target, channel)
            message = '\n'.join(perms) if len(perms) > 0 else 'No permissions'
            await ctx.send(f'Permissions for {target.mention} in {channel.mention}:\n{message}')

def setup(client):
    client.add_cog(Permissions(client))
