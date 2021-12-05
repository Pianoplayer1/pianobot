import aiohttp, asyncio, discord
from .utils import db
from discord.ext import commands
from os import listdir

class Pianobot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix = self._get_prefixes, help_command = None, intents = intents, case_insensitive = True)

        self.load_extension_folder('cogs.commands')
        self.load_extension_folder('cogs.events')
        
        asyncio.get_event_loop().run_until_complete(self._http_session_start())
        self.con = db.connect()

    async def _get_prefixes(self, _, message : discord.Message):
        prefixes = [f'<@!{self.user.id}> ', f'<@{self.user.id}> ']
        if message.guild is None:
            prefixes.append('-')
        else:
            prefixes.extend([prefix for row in self.query("SELECT prefix FROM servers WHERE id = %s", message.guild.id) for prefix in row])
        return prefixes

    def load_extension_folder(self, path : str):
        for extension in [filename[:-3] for filename in listdir(f'./{path.replace(".", "/")}') if filename.endswith('.py')]:
            try:
                self.load_extension(f'{path.replace("/", ".")}.{extension}')
            except Exception as e:
                print(f'Could not load ./{path}/{extension}')
                print(e.__cause__)
    
    def query(self, sql : str, vals : tuple = None) -> tuple:
        return db.query(self.con, sql, vals)

    async def _http_session_start(self):
        self.session = aiohttp.ClientSession()
    async def _http_session_close(self):
        await self.session.close()
    
    def shutdown(self):
        print('Shutting down...')
        asyncio.new_event_loop().run_until_complete(self._http_session_close())
        asyncio.get_event_loop().close()
        db.disconnect(self.con)
        print('Bot exited')