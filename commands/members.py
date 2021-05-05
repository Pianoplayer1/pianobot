from discord.ext import commands
from functions.db import query
from functions.permissions import permissions, check_permissions

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


        output = {  'Dormant, but still in the guild - can be kicked if needed' : [],
                    'Missing link between MC and Discord account' : [],
                    'Wrong amount of Discord roles' : [],
                    'No guild member role in Discord' : [],
                    'Not in the ingame guild' : [],
                    'Highest Discord role not matching ingame role' : [],
                    'Discord nickname not matching ingame name or rank symbol' : []  }

        links = dict(query('SELECT discord, uuid FROM members'))
        async with self.client.session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
            json_response = await response.json()
        ingame_members = {member['uuid'] : {'name': member['name'], 'rank': member['rank']} for member in json_response['members']}

        eden = self.client.get_guild(682671629213368351)
        roles = {   'guild_member' : eden.get_role(682675039631310915),
                    'recruit'      : eden.get_role(703591550424317963),
                    'recruiter'    : eden.get_role(703591538508300299),
                    'captain'      : eden.get_role(682675300307697675),
                    'strategist'   : eden.get_role(727549491699253379),
                    'chief'        : eden.get_role(682675116865224773),
                    'consul'       : eden.get_role(727551690248683571),
                    'owner'        : eden.get_role(682677588933869577) }
        dormant_role = eden.get_role(755160797956669610)
        symbols = {roles['recruit'] : '', roles['recruiter'] : '◉ ', roles['captain'] : '♞ ', roles['strategist'] : '♝ ', roles['chief'] : '♜ ', roles['consul'] : '♕ ', roles['owner'] : '♔ '}
        high_roles = [roles['owner'], roles['consul'], roles['chief'], roles['strategist']]

        for member in eden.members:
            discord_name = member.nick or member.name
            if roles['guild_member'] in member.roles:
                dormant = dormant_role in member.roles
                try:
                    uuid = links[member.id]
                except KeyError:
                    output['Missing link between MC and Discord account'].append(discord_name)
                    continue
                try:
                    ingame_name = ingame_members[uuid]['name']
                    ingame_rank = ingame_members[uuid]['rank'].lower()
                except KeyError:
                    if not dormant:
                        output['Not in the ingame guild'].append(discord_name)
                    continue
                temp_roles = member.roles
                temp_roles.reverse()
                highest_role = next(role for role in temp_roles if role in roles.values())

                if dormant:
                    output['Dormant, but still in the guild - can be kicked if needed'].append(discord_name)

                if sum(role in member.roles for role in roles.values()) != 2:
                    output['Wrong amount of Discord roles'].append(discord_name)

                if highest_role not in [roles[ingame_rank], roles['consul']]:
                    output['Highest Discord role not matching ingame role'].append(discord_name)

                if discord_name != symbols[highest_role] + ingame_members[uuid]['name'] and highest_role not in high_roles:
                    output['Discord nickname not matching ingame name or rank symbol'].append(discord_name)

            elif any(role in member.roles for role in roles.values()) and 'administrator' not in permissions(member, eden.channels[0]):
                output['No guild member role in Discord'].append(discord_name)

        await ctx.send('\n'.join(f'\n**{category[0]}:**\n' + '\n'.join(category[1]) for category in output.items() if len(category[1]) > 0))

def setup(client):
    client.add_cog(Members(client))