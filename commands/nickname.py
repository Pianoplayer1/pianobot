from discord.ext import commands
from functions.permissions import check_permissions

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
        guild = ctx.guild if guild is None else self.client.get_guild(guild)
        if not check_permissions(ctx.author, ctx.channel, ['manage_nicknames']) or 'manage_nicknames' not in permissions(self.client.user, guild.channels[0], guild):
            await ctx.send('You don\'t have the required permissions to edit nicknames!')
            return
        member = guild.get_member(user)
        if member is not None:
            member.edit(nick=nick)
            await ctx.send('Successfully changed the nickname!')
        else:
            await ctx.send('Member could not be found!')
        

def setup(client):
    client.add_cog(Nickname(client))