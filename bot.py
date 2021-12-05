from cogs.bot import Pianobot
from os import getenv

bot = Pianobot()
bot.run(getenv('TOKEN'))
bot.shutdown()