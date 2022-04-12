from os import getenv

from pianobot.db import (
    Connection,
    DiscordMemberTable,
    DiscordRoleTable,
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
        self._con_bot = Connection(
            getenv('PG_DB'),
            getenv('PG_HOST'),
            getenv('PG_PASS'),
            getenv('PG_USER')
        )
        self.guild_activity = GuildActivityTable(self._con_bot)
        self.guild_xp = GuildXPTable(self._con_bot)
        self.guilds = GuildTable(self._con_bot)
        self.member_activity = MemberActivityTable(self._con_bot)
        self.members = MemberTable(self._con_bot)
        self.servers = ServerTable(self._con_bot)
        self.territories = TerritoryTable(self._con_bot)
        self.worlds = WorldTable(self._con_bot)

        self._con_website = Connection(
            getenv('PG_SITE_DB'),
            getenv('PG_SITE_HOST'),
            getenv('PG_SITE_PASS'),
            getenv('PG_SITE_USER')
        )
        self.discord_members = DiscordMemberTable(self._con_website)
        self.discord_roles = DiscordRoleTable(self._con_website)

    def disconnect(self):
        self._con_bot.disconnect()
        self._con_website.disconnect()
