from datetime import datetime
from ..bot import Pianobot

async def run(bot : Pianobot) -> None:
	async with bot.session.get('https://api.wynncraft.com/public_api.php?action=onlinePlayers') as response:
		response = await response.json()
		day = datetime.strftime(datetime.utcnow(), '%Y-%m-%d')
		players = []
		for server in response.values():
			if type(server) == list:
				players.extend(server)
		values = ', '.join(['(\'' + day + '_' + name.lower() + '\', \'' + str(datetime.utcnow()) + '\', 1)' for name in players])
		bot.query(f"INSERT INTO playerActivity VALUES {values} ON DUPLICATE KEY UPDATE count = count + 1")