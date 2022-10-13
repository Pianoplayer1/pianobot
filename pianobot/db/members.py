from uuid import UUID

from pianobot.db import Connection


class Member:
    def __init__(self, uuid: UUID, name: str, rank: str) -> None:
        self._uuid = uuid
        self._name = name
        self._rank = rank

    @property
    def uuid(self) -> UUID:
        return self._uuid

    @property
    def name(self) -> str:
        return self._name

    @property
    def rank(self) -> str:
        return self._rank


class MemberTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    async def get_all(self) -> list[Member]:
        result = await self._con.query('SELECT uuid, name, rank FROM members')
        return [Member(row[0], row[1], row[2]) for row in result]

    async def add(self, uuid: UUID, name: str, rank: str) -> None:
        await self._con.execute(
            f'INSERT INTO members (uuid, name, rank) VALUES ($1, $2, $3)', uuid, name, rank
        )

    async def remove(self, uuid: UUID) -> None:
        await self._con.execute('DELETE FROM members WHERE uuid = $1', uuid)

    async def update_name(self, uuid: UUID, name: str) -> None:
        await self._con.execute('UPDATE members SET name = $1 WHERE uuid = $2', name, uuid)

    async def update_rank(self, uuid: UUID, rank: str) -> None:
        await self._con.execute('UPDATE members SET rank = $1 WHERE uuid = $2', rank, uuid)
