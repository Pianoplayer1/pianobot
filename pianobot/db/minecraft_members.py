from datetime import datetime

from pianobot.db import Connection

class MinecraftMember:
    def __init__(self, uuid, name, rank, joined, last_seen, online, gxp):
        self._uuid = uuid
        self._name = name
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
    def rank(self) -> str:
        return self._rank

    @property
    def joined(self) -> datetime:
        return self._joined

    @property
    def last_seen(self) -> datetime:
        return self._last_seen

    @property
    def online(self) -> bool:
        return self._online

    @property
    def gxp(self) -> int:
        return self._gxp

class MinecraftMemberTable:
    def __init__(self, con: Connection):
        self._con = con

    def get_all(self) -> list[MinecraftMember]:
        res = self._con.query('SELECT * FROM minecraft_members;')
        return [
            MinecraftMember(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in res
        ]

    def add(
        self,
        uuid: str,
        name: str,
        rank: str,
        joined: datetime,
        last_seen: datetime,
        online: bool,
        gxp: int
    ):
        self._con.query(
            'INSERT INTO minecraft_members VALUES (%s, %s, %s, %s, %s, %s, %s);',
            uuid,
            name,
            rank,
            joined,
            last_seen,
            online,
            gxp,
        )

    def update(self, uuid: str, name: str, rank: str, last_seen: datetime, online: bool, gxp: int):
        self._con.query(
            'UPDATE minecraft_members '
            'SET name = %s, rank = %s, last_seen = %s, online = %s, xp = %s '
            'WHERE uuid = %s;',
            name,
            rank,
            last_seen,
            online,
            gxp,
            uuid
        )

    def remove(self, uuid: str):
        self._con.query('DELETE FROM minecraft_members WHERE uuid = %s;', uuid)
