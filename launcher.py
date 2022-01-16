from logging import basicConfig, getLogger, WARNING, ERROR
from os import getenv

from pianobot import Pianobot

basicConfig(level = WARNING)
getLogger("discord.gateway").setLevel(ERROR)

bot = Pianobot()
bot.run(getenv('TOKEN'))
bot.shutdown()
