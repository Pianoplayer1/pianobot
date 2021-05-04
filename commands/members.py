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
        output = {'Missing link':[],'Wrong amount of roles':[],'No guild member role':[],'Not in the guild':[],'Wrong role':[]}

        links = dict(query('SELECT discord, uuid FROM members'))
        async with self.client.session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
            json_response = await response.json()
        ingame_members = {member['uuid'] : {'name': member['name'], 'rank': member['rank']} for member in json_response['members']}

        eden = self.client.get_guild(682671629213368351)
        roles = {'guild_member' : eden.get_role(682675039631310915),
                 'recruit'      : eden.get_role(703591550424317963),
                 'recruiter'    : eden.get_role(703591538508300299),
                 'captain'      : eden.get_role(682675300307697675),
                 'strategist'   : eden.get_role(727549491699253379),
                 'chief'        : eden.get_role(682675116865224773),
                 'consul'       : eden.get_role(727551690248683571),
                 'owner'        : eden.get_role(682677588933869577)}

        for member in eden.members:
            if roles['guild_member'] in member.roles:
                if sum(role in member.roles for role in roles.values()) > 2:
                    output['Wrong amount of roles'].append(member.nick)
                try:
                    uuid = links[member.id]
                    try:
                        ingame_member = ingame_members[uuid]
                        if roles[ingame_member['rank'].lower()] in member.roles:
                            a=1
                        else:
                            output['Wrong role'].append(member.nick)
                    except KeyError:
                        output['Not in the guild'].append(member.nick)
                except KeyError:
                    output['Missing link'].append(member.nick)
            elif any(role in member.roles for role in roles.values()):
                output['No guild member role'].append(member.nick)

        await ctx.send(output)

def setup(client):
    client.add_cog(Members(client))