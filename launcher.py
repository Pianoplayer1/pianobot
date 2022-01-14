from logging import basicConfig, WARNING
from os import getenv

from pianobot import Pianobot

basicConfig(level = WARNING)

bot = Pianobot()
bot.run(getenv('TOKEN'))
bot.shutdown()
