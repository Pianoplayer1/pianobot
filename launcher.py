from logging import basicConfig, WARNING
from os import getenv

from cogs.bot import Pianobot

basicConfig(level=WARNING)

bot = Pianobot()
bot.run(getenv('TOKEN'))
bot.shutdown()
