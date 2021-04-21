from datetime import datetime
import aiohttp, asyncio

async def fetch(session, member):
    async with session.get(f'https://api.wynncraft.com/v2/player/{member["uuid"]}/stats') as response:
        memberStats = await response.json()
        if memberStats['code'] != 200:
            print(f'Member {member["name"]} could not be found.')
        else:
            if memberStats['data'][0]['meta']['location']['online'] == True:
                times[member['name']] = [0, 'Online']
            else:
                diff = datetime.strptime(str(datetime.utcnow()), '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(memberStats['data'][0]['meta']['lastJoin'], '%Y-%m-%dT%H:%M:%S.%fZ')
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
                times[member['name']] = [days, str(int(round(value))) + append]
            ranks[member['name']] = member['rank'].title()
            
async def check_activity(guild, reverse):
    global times
    global final_times
    global ranks
    times = {}
    final_times = {}
    ranks = {}
    async with aiohttp.ClientSession() as session, session.get(f'https://api.wynncraft.com/public_api.php?action=guildStats&command={guild}') as response:
        guildStats = await response.json()
        await asyncio.gather(*[fetch(session, member) for member in guildStats['members']])

    data = []
    for key, value in sorted(times.items(), key=lambda item: item[1][0], reverse=reverse):
        data.append([key, ranks[key], times[key][1]])
    return data