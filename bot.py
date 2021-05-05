import aiohttp, asyncio, discord
from discord.ext import commands
from functions import db
from os import listdir, getenv

class Pianobot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix = self.get_prefixes, help_command = None, intents = intents)

        self.load_extension_folder('commands')
        self.load_extension_folder('events')

        asyncio.get_event_loop().run_until_complete(self.http_session_start())
        db.connect()

    async def get_prefixes(self, client, message):
        prefixes = [f'<@!{self.user.id}> ', f'<@{self.user.id}> ']
        if message.guild is None:
            prefixes.append('-')
        else:
            prefixes.extend([prefix for row in db.query("SELECT prefix FROM servers WHERE id = %s", message.guild.id) for prefix in row])
        return prefixes

    def load_extension_folder(self, path):
        for extension in [filename[:-3] for filename in listdir(f'./{path}') if filename.endswith('.py')]:
            try:
                self.load_extension(f'{path.replace("/", ".")}.{extension}')
            except Exception as e:
                print(f'Could not load ./{path}/{extension}')

    async def http_session_start(self):
        self.session = aiohttp.ClientSession()
    async def http_session_close(self):
        await self.session.close()

    def shutdown(self):
        print('Shutting down...')
        asyncio.create_event_loop().run_until_complete(self.http_session_close())
        db.disconnect()
        print('Bot exited')

client = Pianobot()
client.run(getenv('TOKEN'))
client.shutdown()