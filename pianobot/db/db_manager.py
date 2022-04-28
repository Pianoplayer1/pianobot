from os import getenv

from pianobot.db import (
    Connection,
    GuildActivityTable,
    GuildXPTable,
    MemberActivityTable,
    ServerTable,
    TerritoryTable,
    WorldTable,
)


class DBManager:
    def __init__(self):
        self._con_bot = Connection(
            getenv('PG_DB', 'pianobot'),
            getenv('PG_HOST', 'localhost'),
            getenv('PG_PASS', ''),
            getenv('PG_USER', 'root'),
        )
        self.guild_activity = GuildActivityTable(self._con_bot)
        self.guild_xp = GuildXPTable(self._con_bot)
        self.member_activity = MemberActivityTable(self._con_bot)
        self.servers = ServerTable(self._con_bot)
        self.territories = TerritoryTable(self._con_bot)
        self.worlds = WorldTable(self._con_bot)

    async def connect(self) -> None:
        await self._con_bot.connect()

    async def disconnect(self) -> None:
        await self._con_bot.disconnect()
