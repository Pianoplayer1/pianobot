from discord.ext import commands
from functions.db import query
from functions.db import check_permissions

class Members(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(  name = 'members',
                        aliases = [],
                        brief = 'Outputs members of the Eden Discord server.',
                        help = 'This command outputs members of the Eden Discord server.',
                        usage = ''  )
    async def members(self, ctx, *, args = None):
        if args is not None and check_permissions(ctx.author, ctx.channel, ['manage_roles']):
            command, name, id = args.split()
            if command.lower() == 'link':
                async with self.client.session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as response:
                    json_response = await response.json()
                uuid = json_response['id']
                name = json_response['name']
                if uuid:
                    uuid = uuid[0:8]+'-'+uuid[8:12]+'-'+uuid[12:16]+'-'+uuid[16:20]+'-'+uuid[20:32]
                    query('INSERT INTO members VALUES(%s, %s, %s, 0, 0, 0, 0, 0)', (name, uuid, id))
                else:
                    print(f'Couldn\'t find uuid of {name}')
                return
        output = {'Missing link':[],'Wrong amount of roles':[],'No guild member role':[],'Not in the guild':[],'Wrong role':[],'Wrong nickname':[]}

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
        high_roles = [roles['owner'], roles['consul'], roles['chief'], roles['strategist']]

        for member in eden.members:
            if roles['guild_member'] in member.roles:
                if sum(role in member.roles for role in roles.values()) != 2:
                    output['Wrong amount of roles'].append(member.nick or member.name)
                try:
                    uuid = links[member.id]
                    try:
                        ingame_member = ingame_members[uuid]
                        if any(role in member.roles for role in [roles[ingame_member['rank'].lower()], roles['consul']]):
                            if ingame_member['name'] not in (member.nick or member.name) and all(role not in member.roles for role in [high_roles]):
                                output['Wrong nickname'].append(member.nick or member.name)
                        else:
                            output['Wrong role'].append(member.nick or member.name)
                    except KeyError:
                        output['Not in the guild'].append(member.nick or member.name)
                except KeyError:
                    output['Missing link'].append(member.nick or member.name)
            elif any(role in member.roles for role in roles.values()) and not check_permissions(member, ctx.channel, ['administrator']):
                output['No guild member role'].append(member.nick or member.name)
        message = ''
        for category in output.items():
            message += f'\n\n**{category[0]}:**\n'
            message += '\n'.join(category[1])
        await ctx.send(message)

def setup(client):
    client.add_cog(Members(client))