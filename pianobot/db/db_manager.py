from pianobot.db import (
    Connection,
    GuildActivityTable,
    GuildXPTable,
    GuildTable,
    MemberActivityTable,
    MemberTable,
    ServerTable,
    TerritoryTable,
    WorldTable
)

class DBManager:
    def __init__(self):
        self._con = Connection()
        self.guild_activity = GuildActivityTable(self._con)
        self.guild_xp = GuildXPTable(self._con)
        self.guilds = GuildTable(self._con)
        self.member_activity = MemberActivityTable(self._con)
        self.members = MemberTable(self._con)
        self.servers = ServerTable(self._con)
        self.territories = TerritoryTable(self._con)
        self.worlds = WorldTable(self._con)

    def disconnect(self):
        self._con.disconnect()
