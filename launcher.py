from cogs.bot import Pianobot
from os import getenv
import logging

logging.basicConfig(level=logging.WARNING)

bot = Pianobot()
bot.run(getenv('TOKEN'))
bot.shutdown()