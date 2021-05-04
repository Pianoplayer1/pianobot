from discord.ext import commands
from functions.db import query

class Members(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(  name = 'members',
                        aliases = [],
                        brief = 'Outputs members of the Eden Discord server.',
                        help = 'This command outputs members of the Eden Discord server.',
                        usage = ''  )
    async def members(self, ctx):
        output = {'Missing link' : [], 'Wrong amount of roles' : []}

        links = dict(query('SELECT uuid, discord FROM members'))
        async with self.client.session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
            ingame_members = await response.json()
            ingame_members = ingame_members['members']
        for member in ingame_members:
            try:
                if links[member['uuid']] == 0:
                    raise KeyError
            except KeyError:
                output['Missing link'].append(member['name'])

        eden = self.client.get_guild(682671629213368351)
        roles = {'guild_member' : eden.get_role(682675039631310915),
                 'citizen'      : eden.get_role(703591550424317963),
                 'legionnaire'  : eden.get_role(703591538508300299),
                 'legate'       : eden.get_role(682675300307697675),
                 'senate'       : eden.get_role(727549491699253379),
                 'dux'          : eden.get_role(682675116865224773),
                 'consul'       : eden.get_role(727551690248683571),
                 'emperor'      : eden.get_role(682677588933869577)}
        discord_members = [member for member in eden.members if roles['guild_member'] in member.roles]
        output['Wrong amount of roles'] = [member.nick for member in discord_members if sum(role in member.roles for role in roles.values()) > 2]

        await ctx.send(output)

def setup(client):
    client.add_cog(Members(client))