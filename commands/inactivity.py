import aiohttp, asyncio
from datetime import datetime
from discord.ext import commands
from functions.pages import paginator
from functions.permissions import check_permissions
from functions.table import table

class Inactivity(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(  name = 'inactivity',
                        aliases = ['act', 'activity', 'inact'],
                        brief = 'Outputs the member inactivity times of a specified guild.',
                        help = 'This command returns a table with the times since each member of a specified guild has been last seen on the Wynncraft server.',
                        usage = '<guild>'  )
    async def inactivity(self, ctx, *, guild):
        async with self.client.session.get(f'https://api.wynncraft.com/public_api.php?action=guildList') as response:
            guilds = await response.json()
            guilds = guilds['guilds']
            try:
                matches = [guilds[list(map(str.lower, guilds)).index(guild.lower())]]
            except ValueError:
                matches = [g for g in guilds if guild.lower() in g.lower()]
            if len(matches) == 0:
                await ctx.send(f'No guild names include \'{guild}\'. Please try again with another guild name.')
                return
            elif len(matches) == 1:
                guild = matches[0]
                message = None
            elif len(matches) <= 5:
                message = f'Several guild names include \'{guild}\'. Enter the number of one of the following guilds to view their inactivity.\nTo leave this prompt, type \'exit\'.\n'
                for match in range(len(matches)):
                    message += f'\n{match + 1}. {matches[match]}'
                message = await ctx.send(message)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                msg = await self.client.wait_for('message', check=check)
                if ctx.guild and check_permissions(self.client.user, ctx.channel, ['manage_messages']):
                    await msg.delete()
                
                try:
                    guild = matches[int(msg.content) - 1]
                except (IndexError, ValueError):
                    if msg.content == 'exit':
                        await message.edit(content = 'Prompt exited.')
                    else:
                        await message.edit(content = 'Invalid input, exited prompt.')
                    return
            else:
                await ctx.send(f'Several guild names include \'{guild}\'. Please try again with a more precise name.')
                return
            
            self.times = {}
            self.ranks = {}
            async with self.client.session.get(f'https://api.wynncraft.com/public_api.php?action=guildStats&command={guild}') as response:
                guildStats = await response.json()
                await asyncio.gather(*[self.fetch(member) for member in guildStats['members']])

            columns = {f'{guild} Members' : 36, 'Rank' : 26, 'Time Inactive' : 26}
            ascending_data = [[key, self.ranks[key], self.times[key][1]] for key, value in sorted(self.times.items(), key=lambda item: item[1][0])]
            descending_data = [[key, self.ranks[key], self.times[key][1]] for key, value in sorted(self.times.items(), key=lambda item: item[1][0], reverse=True)]
            ascending_table = table(columns, ascending_data, 5, 15, True, '(Ascending Order)')
            descending_table = table(columns, descending_data, 5, 15, True, '(Descending Order)')
            await paginator(self.client, ctx, descending_table, message, ascending_table)

    async def fetch(self, member):
        async with self.client.session.get(f'https://api.wynncraft.com/v2/player/{member["uuid"]}/stats') as response:
            memberStats = await response.json()
            if memberStats['code'] != 200:
                print(f'Member {member["name"]} could not be found.')
            else:
                if memberStats['data'][0]['meta']['location']['online'] == True:
                    self.times[member['name']] = [0, 'Online']
                else:
                    diff = datetime.utcnow() - datetime.strptime(memberStats['data'][0]['meta']['lastJoin'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    days = diff.days + (diff.seconds / 86400)
                    value = days
                    if value < 1:
                        value *= 24
                        if value < 1:
                            value *= 60
                            append = ' minute'
                        else:
                            append = ' hour'
                    else:
                        append = ' day'
                    if round(value) != 1:
                        append += 's'
                    self.times[member['name']] = [days, str(int(round(value))) + append]
                self.ranks[member['name']] = member['rank'].title()

def setup(client):
    client.add_cog(Inactivity(client))