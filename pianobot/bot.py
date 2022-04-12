from logging import getLogger
from os import listdir

from corkus import Corkus

from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands.errors import ExtensionFailed

from pianobot.db.db_manager import DBManager
from pianobot.utils import get_prefix

class Pianobot(commands.Bot):
    def __init__(self) -> None:
        intents = Intents.default()
        intents.members = True
        super().__init__(
            case_insensitive=True,
            command_prefix=self._get_prefixes,
            help_command=None,
            intents=intents
        )

        self._load_extension_folder('pianobot.commands')
        self._load_extension_folder('pianobot.events')

        self.corkus = Corkus()
        self.database = DBManager()
        self.logger = getLogger('bot')

        with open('tracked_guilds.txt', 'r', encoding='UTF-8') as file:
            self.tracked_guilds = {
                name: tag for line in file for (name, tag) in [line.strip().split(':')]
            }

    async def _get_prefixes(self, _, message: Message) -> list[str]:
        prefixes = [
            f'<@!{self.user.id}> ',
            f'<@{self.user.id}> ',
            f'<@!{self.user.id}>',
            f'<@{self.user.id}>'
        ]
        prefixes.append(get_prefix(self.database.servers, message.guild))
        return prefixes

    def _load_extension_folder(self, path: str) -> None:
        files = listdir(f'./{path.replace(".", "/")}')
        for extension in [file[:-3] for file in files if file.endswith('.py')]:
            try:
                self.load_extension(f'{path.replace("/", ".")}.{extension}')
            except ExtensionFailed as exc:
                self.logger.warning('Could not load ./%s/%s\n%s', path, extension, exc.__cause__)

    def shutdown(self) -> None:
        self.database.disconnect()
        self.logger.info('Bot exited')
