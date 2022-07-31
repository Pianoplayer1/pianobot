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
    def __init__(self) -> None:
        self._con = Connection(
            getenv('PG_DB', 'pianobot'),
            getenv('PG_HOST', 'localhost'),
            getenv('PG_PASS', ''),
            getenv('PG_USER', 'root'),
        )
        self.guild_activity = GuildActivityTable(self._con)
        self.guild_xp = GuildXPTable(self._con)
        self.member_activity = MemberActivityTable(self._con)
        self.servers = ServerTable(self._con)
        self.territories = TerritoryTable(self._con)
        self.worlds = WorldTable(self._con)

    async def connect(self) -> None:
        await self._con.connect()

    async def disconnect(self) -> None:
        await self._con.disconnect()
