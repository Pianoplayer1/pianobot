from logging import getLogger
from os import listdir

from aiohttp import ClientSession
from corkus import Corkus
from discord import Intents, Message
from discord.ext.commands import Bot, when_mentioned_or
from discord.ext.commands.errors import ExtensionFailed

from pianobot.db.db_manager import DBManager
from pianobot.tasks import TaskRunner
from pianobot.utils import get_prefix


class Pianobot(Bot):
    def __init__(self) -> None:
        intents = Intents.default()
        intents.members = True
        intents.message_content = True

        async def _get_prefixes(bot: Bot, message: Message) -> list[str]:
            prefix = await get_prefix(self.database.servers, message.guild)
            return when_mentioned_or(prefix)(bot, message)

        super().__init__(
            case_insensitive=True,
            command_prefix=_get_prefixes,
            help_command=None,
            intents=intents,
        )

        self.logger = getLogger('bot')
        self.corkus: Corkus = None
        self.database = DBManager()
        self.enable_tracking = False
        self.session: ClientSession = None

        with open('tracked_guilds.txt', 'r', encoding='UTF-8') as file:
            self.tracked_guilds: dict[str, str] = {
                name: tag for line in file for (name, tag) in [line.strip().split(':')]
            }

    async def setup_hook(self) -> None:
        await self.database.connect()
        self.session = ClientSession()
        self.corkus = Corkus()
        await TaskRunner(self).start_tasks()

        for folder in ['commands', 'events']:
            for extension in [f[:-3] for f in listdir(f'pianobot/{folder}') if f.endswith('.py')]:
                try:
                    await self.load_extension(f'pianobot.{folder}.{extension}')
                except ExtensionFailed as exc:
                    self.logger.warning('Skipped %s.%s: %s', folder, extension, exc.__cause__)

    async def on_ready(self):
        self.logger.info('Booted up')

    async def close(self):
        await self.corkus.close()
        await self.database.disconnect()
        self.logger.info('Exited')
        await super().close()
