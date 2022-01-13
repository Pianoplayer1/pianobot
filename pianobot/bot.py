from os import listdir

from corkus import Corkus

from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands.errors import ExtensionFailed

from pianobot.db.db_manager import DBManager

class Pianobot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix = self._get_prefixes,
            help_command = None,
            intents = Intents.all(),
            case_insensitive = True
        )

        self._load_extension_folder('pianobot.commands')
        self._load_extension_folder('pianobot.events')

        self.corkus = Corkus()
        self.database = DBManager()

        with open('tracked_guild.txt', 'r', encoding = 'UTF-8') as file:
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
        if message.guild is None:
            prefixes.append('-')
        else:
            server = self.database.servers.get(message.guild.id)
            if server:
                prefixes.append(server.prefix)
        return prefixes

    def _load_extension_folder(self, path: str) -> None:
        files = listdir(f'./{path.replace(".", "/")}')
        for extension in [file[:-3] for file in files if file.endswith('.py')]:
            try:
                self.load_extension(f'{path.replace("/", ".")}.{extension}')
            except ExtensionFailed as exc:
                print(f'Could not load ./{path}/{extension}')
                print(exc.__cause__)

    def shutdown(self) -> None:
        self.database.disconnect()
        print('Bot exited')
