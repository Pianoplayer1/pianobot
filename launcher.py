from logging import basicConfig
from os import getenv

from cogs.bot import Pianobot

basicConfig(level=logging.WARNING)

bot = Pianobot()
bot.run(getenv('TOKEN'))
bot.shutdown()
