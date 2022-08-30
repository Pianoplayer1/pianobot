import logging
import os

from pianobot import Pianobot


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('discord').setLevel(logging.WARNING)

    bot = Pianobot()
    bot.run(os.getenv('TOKEN') or '', log_handler=None)


if __name__ == '__main__':
    main()
