from ..bot import Pianobot
from discord.ext import commands
from ..utils.permissions import check_permissions

class Members(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot

    @commands.command(  name = 'members',
                        aliases = [],
                        brief = 'Outputs members of the Eden Discord server.',
                        help = 'This command outputs members of the Eden Discord server.',
                        usage = '')
    async def members(self, ctx : commands.Context, *, args : str = None):
        links = dict(self.bot.query('SELECT `discord`, `uuid` FROM `members`;'))
        links_r = dict(self.bot.query('SELECT `uuid`, `discord` FROM `members`;'))

        if args and check_permissions(ctx.author, ctx.channel, 'manage_roles'):
            command, name, discord_id = args.split()
            if command.lower() == 'link':
                async with self.bot.session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as response:
                    json_response = await response.json()
                try:
                    uuid = json_response['id']
                    name = json_response['name']
                except KeyError:
                    await ctx.send(f'Couldn\'t find uuid of {name}')
                    return

                uuid = uuid[0:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:32]
                if uuid in links.values():
                    self.bot.query('UPDATE members SET discord=%s WHERE uuid=%s;', (discord_id, uuid))
                else:
                    self.bot.query('INSERT INTO members VALUES(%s, %s, %s, 0, 0, 0, 0, 0);', (uuid, name, discord_id))
            return


        output = {  'Dormant, but still in the guild - can be kicked if needed' : [],
                    'Not linked to a minecraft account' : [],
                    'Unknown Discord account' : [],
                    'Wrong amount of Discord roles' : [],
                    'No guild member role in Discord' : [],
                    'Not in the ingame guild' : [],
                    'Highest Discord role not matching ingame role' : [],
                    'Discord nickname not matching ingame name or rank symbol' : []  }

        eden = self.bot.get_guild(682671629213368351)
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

        async with self.bot.session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
            json_response = await response.json()
        ingame_members = {}
        for member in json_response['members']:
            if member['uuid'] not in links.values() or links_r[member['uuid']] == 0:
                output['Unknown Discord account'].append(member['name'].replace('_', '\_') + f' ({member["uuid"]})')
            else:
                ingame_members[member['uuid']] = {'name': member['name'], 'rank': member['rank']}

        for member in eden.members:
            discord_name = member.nick or member.name
            message_name = discord_name if any(role in senate_roles for role in member.roles) else member.mention
            if roles['guild_member'] in member.roles:
                is_dormant = dormant_role in member.roles
                try:
                    uuid = links[member.id]
                    if not is_dormant:
                        links.pop(member.id)
                    if uuid == '0':
                        raise KeyError
                except KeyError:
                    if not is_dormant:
                        output['Not linked to a minecraft account'].append(message_name)
                    continue
                try:
                    ingame_name = ingame_members[uuid]['name']
                    ingame_rank = ingame_members[uuid]['rank'].lower()
                except KeyError:
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

            elif any(role in member.roles for role in roles.values()) and not check_permissions(member, eden.channels[0], 'administrator'):
                output['No guild member role in Discord'].append(message_name)

        await ctx.send('\n'.join(f'\n**{category[0]}:**\n' + '\n'.join(category[1]) for category in output.items() if len(category[1]) > 0))

        for discord, uuid in links.items():
            if uuid not in ingame_members.keys():
                self.bot.query('DELETE FROM `members` WHERE `discord` = %s;', discord)
                print('Deleted', uuid, discord)

def setup(bot : Pianobot):
    bot.add_cog(Members(bot))