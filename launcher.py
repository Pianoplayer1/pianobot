import logging
import os

from pianobot import Pianobot


def main() -> None:
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logging.getLogger('discord.gateway').setLevel(logging.WARNING)

    bot = Pianobot()
    bot.run(os.getenv('TOKEN') or '', log_handler=None)


if __name__ == '__main__':
    main()
