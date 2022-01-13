from logging import basicConfig, INFO
from os import getenv

from pianobot import Pianobot

basicConfig(level = INFO)

bot = Pianobot()
bot.run(getenv('TOKEN'))
bot.shutdown()
