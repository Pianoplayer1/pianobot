from corkus.objects.leaderboard_guild import LeaderboardGuild

from pianobot.db import Connection

class Guild:
    def __init__(self, name, tag, level, gxp, territories, warcount, members, created):
        self._name = name
        self._tag = tag
        self._level = level
        self._gxp = gxp
        self._territories = territories
        self._warcount = warcount
        self._members = members
        self._created = created

    @property
    def name(self) -> str:
        return self._name

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def level(self) -> int:
        return self._level

    @property
    def gxp(self) -> int:
        return self._gxp

    @property
    def territories(self) -> int:
        return self._territories

    @property
    def warcount(self) -> int:
        return self._warcount

    @property
    def members(self) -> int:
        return self._members

    @property
    def created(self) -> int:
        return self._created

class GuildTable:
    def __init__(self, con: Connection):
        self._con = con

    def delete_all(self):
        self._con.query('TRUNCATE TABLE guilds;')

    def add(self, data: list[LeaderboardGuild]):
        placeholders = ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s)' for _ in data])
        args = []
        for guild in data:
            args.extend((
                guild.name,
                guild.tag,
                guild.level,
                guild.total_xp,
                guild.territories.count,
                guild.war_count,
                guild.members_count,
                guild.created
            ))
        self._con.query(f'INSERT INTO guilds VALUES {placeholders};', *args)
