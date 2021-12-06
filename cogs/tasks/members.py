from ..bot import Pianobot
from datetime import datetime

async def run(bot : Pianobot) -> None:
    db_members = dict(bot.query("SELECT uuid, name FROM members"))
    async with bot.session.get('https://api.wynncraft.com/public_api.php?action=guildStats&command=Eden') as response:
        eden = await response.json()
        for member in eden['members']:
            if member['uuid'] not in db_members:
                epoch = (datetime.strptime(member['joined'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
                bot.query("INSERT INTO members(uuid, joined) VALUES (%s, %s)", (member['uuid'], epoch))
            bot.query("UPDATE members SET name=%s, rank=%s, xp=%s WHERE uuid=%s", (member['name'], member['rank'].capitalize(), member['contributed'], member['uuid']))