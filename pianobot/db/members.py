from pianobot.db import Connection

class Member:
    def __init__(self, uuid, name, discord, rank, joined, last_seen, online, gxp):
        self._uuid = uuid
        self._name = name
        self._discord = discord
        self._rank = rank
        self._joined = joined
        self._last_seen = last_seen
        self._online = online
        self._gxp = gxp

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def name(self) -> str:
        return self._name

    @property
    def discord(self) -> int:
        return self._discord

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def joined(self) -> int:
        return self._joined

    @property
    def last_seen(self) -> int:
        return self._last_seen

    @property
    def members(self) -> int:
        return self._online

    @property
    def gxp(self) -> int:
        return self._gxp

class MemberTable:
    def __init__(self, con: Connection):
        self._con = con

    def get_all(self) -> list[Member]:
        result = self._con.query('SELECT * FROM members;')
        return [
            Member(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in result
        ]

    def add(self, uuid: str, joined: int):
        self._con.query('INSERT INTO members (uuid, joined) VALUES (%s, %s);', uuid, joined)

    def update(self, name: str, rank: int, gxp: int, uuid: str):
        self._con.query(
            'UPDATE members SET name = %s, rank = %s, xp = %s WHERE uuid = %s;',
            name,
            rank,
            gxp,
            uuid
        )
