from logging import basicConfig, getLogger, ERROR, INFO
from os import getenv

from pianobot import Pianobot

def main():
    basicConfig(level=INFO)
    getLogger('discord.gateway').setLevel(ERROR)

    bot = Pianobot()
    bot.run(getenv('TOKEN'))
    bot.shutdown()

if __name__ == '__main__':
    main()
