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
            try:
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
                        await ctx.send(f'Couldn\'t find uuid of {name}')
            finally:
                return


        output = {  'Dormant, but still in the guild - can be kicked if needed' : [],
                    'Not linked to a minecraft account' : [],
                    'Unknown Discord account' : [],
                    'Wrong amount of Discord roles' : [],
                    'No guild member role in Discord' : [],
                    'Not in the ingame guild' : [],
                    'Highest Discord role not matching ingame role' : [],
                    'Discord nickname not matching ingame name or rank symbol' : []  }
        
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
        rank_symbols = {roles['recruit'] : '', roles['recruiter'] : '◉ ', roles['captain'] : '♞ ', roles['strategist'] : '♝ ', roles['chief'] : '♜ ', roles['consul'] : '♕ ', roles['owner'] : '♔ '}
        senate_roles = [roles['owner'], roles['consul'], roles['chief'], roles['strategist']]

        links = dict(query('SELECT discord, uuid FROM members'))
        async with self.client.session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
            json_response = await response.json()
        ingame_members = {}
        for member in json_response['members']:
            if member['uuid'] not in links.values():
                output['Unknown Discord account'].append(member['name'].replace('_', '\_'))
            else:
                ingame_members[member['uuid']] = {'name': member['name'], 'rank': member['rank']}

        for member in eden.members:
            discord_name = member.nick or member.name
            message_name = discord_name if any(role in senate_roles for role in member.roles) else member.mention
            if roles['guild_member'] in member.roles:
                is_dormant = dormant_role in member.roles
                try:
                    uuid = links[member.id]
                    links.pop(member.id)
                    if uuid == '0':
                        raise KeyError
                except KeyError:
                    output['Not linked to a minecraft account'].append(message_name)
                    continue
                try:
                    ingame_name = ingame_members[uuid]['name']
                    ingame_rank = ingame_members[uuid]['rank'].lower()
                except KeyError:
                    if not is_dormant:
                        output['Not in the ingame guild'].append(message_name)
                    continue
                temp_roles = member.roles
                temp_roles.reverse()
                highest_role = next(role for role in temp_roles if role in roles.values())

                if is_dormant:
                    output['Dormant, but still in the guild - can be kicked if needed'].append(message_name)

                if sum(role in member.roles for role in roles.values()) != 2:
                    output['Wrong amount of Discord roles'].append(message_name)

                if highest_role in senate_roles:
                    continue

                if highest_role != roles[ingame_rank]:
                    output['Highest Discord role not matching ingame role'].append(f'{message_name} ({ingame_rank} ingame)')

                correct_name = rank_symbols[highest_role] + ingame_members[uuid]['name']
                if discord_name != correct_name:
                    output['Discord nickname not matching ingame name or rank symbol'].append(message_name + ' --> ' + correct_name.replace('_', '\_'))

            elif any(role in member.roles for role in roles.values()) and 'administrator' not in permissions(member, eden.channels[0]):
                output['No guild member role in Discord'].append(message_name)

        await ctx.send('\n'.join(f'\n**{category[0]}:**\n' + '\n'.join(category[1]) for category in output.items() if len(category[1]) > 0))

        for uuid in links.keys():
            if uuid not in ingame_members.keys():
                query('DELETE FROM members WHERE discord = %s', links[uuid])
                print('Deleted', uuid, links[uuid])

def setup(client):
    client.add_cog(Members(client))
