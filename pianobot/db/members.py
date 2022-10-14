from datetime import datetime
from uuid import UUID

from pianobot.db import Connection


class Member:
    def __init__(
        self, uuid: UUID, join_date: datetime, name: str, rank: str, contributed_xp: int
    ) -> None:
        self._uuid = uuid
        self._join_date = join_date
        self._name = name
        self._rank = rank
        self._contributed_xp = contributed_xp

    @property
    def uuid(self) -> UUID:
        return self._uuid

    @property
    def join_date(self) -> datetime:
        return self._join_date

    @property
    def name(self) -> str:
        return self._name

    @property
    def rank(self) -> str:
        return self._rank

    @property
    def contributed_xp(self) -> int:
        return self._contributed_xp


class MemberTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    async def get_all(self) -> list[Member]:
        result = await self._con.query(
            'SELECT uuid, join_date, name, rank, contributed_xp FROM members'
        )
        return [Member(row[0], row[1], row[2], row[3], row[4]) for row in result]

    async def add(
        self, uuid: UUID, joined_at: datetime, name: str, rank: str, contributed_xp: int
    ) -> None:
        await self._con.execute(
            f'INSERT INTO members (uuid, name, join_date, rank, contributed_xp)'
            f' VALUES ($1, $2, $3, $4, $5)',
            uuid,
            joined_at,
            name,
            rank,
            contributed_xp,
        )

    async def remove(self, uuid: UUID) -> None:
        await self._con.execute('DELETE FROM members WHERE uuid = $1', uuid)

    async def update_name(self, uuid: UUID, name: str) -> None:
        await self._con.execute('UPDATE members SET name = $1 WHERE uuid = $2', name, uuid)

    async def update_rank(self, uuid: UUID, rank: str) -> None:
        await self._con.execute('UPDATE members SET rank = $1 WHERE uuid = $2', rank, uuid)

    async def update_contributed_xp(self, uuid: UUID, contributed_xp: int) -> None:
        await self._con.execute(
            'UPDATE members SET contributed_xp = $1 WHERE uuid = $2', contributed_xp, uuid
        )
