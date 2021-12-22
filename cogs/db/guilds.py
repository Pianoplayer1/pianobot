from corkus.objects.leaderboard_guild import LeaderboardGuild

from .connection import Connection

class Guild:
    def __init__(self, name, tag, level, xp, territories, warcount, members, created):
        self._name = name
        self._tag = tag
        self._level = level
        self._xp = xp
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
    def xp(self) -> int:
        return self._xp
    
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

class Manager:
    def __init__(self, db: Connection):
        self._db = db

    def delete_all(self):
        self._db.query('TRUNCATE TABLE guilds;')
    
    def add(self, data: list[LeaderboardGuild]):
        placeholders = ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s)' for _ in data])
        args = []
        for g in data:
            args.extend((g.name, g.tag, g.level, g.total_xp, g.territories.count, g.war_count, g.members_count, g.created))
        self._db.query(f'INSERT INTO guilds VALUES {placeholders};', *args)
