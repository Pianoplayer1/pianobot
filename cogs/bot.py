from os import listdir

from corkus import Corkus

from discord import Intents, Message
from discord.ext import commands

from .db import db_manager

class Pianobot(commands.Bot):
    def __init__(self):
        intents = Intents.default()
        intents.members = True
        super().__init__(command_prefix=self._get_prefixes, help_command=None, intents=intents, case_insensitive=True)

        self.load_extension_folder('cogs.commands')
        self.load_extension_folder('cogs.events')
        
        self.corkus = Corkus()
        self.db = db_manager.DBManager()

    async def _get_prefixes(self, _, message: Message) -> list[str]:
        prefixes = [f'<@!{self.user.id}> ', f'<@{self.user.id}> ', f'<@!{self.user.id}>', f'<@{self.user.id}>']
        if message.guild is None:
            prefixes.append('-')
        else:
            server = self.db.servers.get(message.guild.id)
            if server:
                prefixes.append(server.prefix)
        return prefixes

    def load_extension_folder(self, path: str):
        for extension in [filename[:-3] for filename in listdir(f'./{path.replace(".", "/")}') if filename.endswith('.py')]:
            try:
                self.load_extension(f'{path.replace("/", ".")}.{extension}')
            except Exception as e:
                print(f'Could not load ./{path}/{extension}')
                print(e.__cause__)

    def shutdown(self):
        self.db.disconnect()
        print('Bot exited')
