from logging import basicConfig, INFO
from os import getenv

from cogs.bot import Pianobot

basicConfig(level=INFO)

bot = Pianobot()
bot.run(getenv('TOKEN'))
bot.shutdown()
