from discord.ext import commands
from ..utils.permissions import permissions, check_permissions

class Nickname(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(  name = 'nickname',
                        aliases = ['nick'],
                        brief = 'Change a member\'s nickname.',
                        help = 'Change the nickname of a user by passing their user id and the new nickname.',
                        usage = '<user id> <nickname> [guild id]',
                        hidden = True  )
    @commands.guild_only()
    async def nickname(self, ctx, user, nick, guild = None):
        guild = ctx.guild if not guild else self.client.get_guild(guild)
        if check_permissions(self.client.user, ctx.channel, ['manage_nicknames']):
            await ctx.send('I don\'t have the required permissions to edit nicknames!')
            return
        member = guild.get_member(int(user))
        if member:
            await member.edit(nick=nick)
            await ctx.send('Successfully changed the nickname!')
        else:
            await ctx.send('Member could not be found!')
        

def setup(client):
    client.add_cog(Nickname(client))