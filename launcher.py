import logging
import os

from pianobot import Pianobot

def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('discord').setLevel(logging.WARNING)

    bot = Pianobot()
    bot.run(os.getenv('TOKEN'))
    bot.shutdown()

if __name__ == '__main__':
    main()
