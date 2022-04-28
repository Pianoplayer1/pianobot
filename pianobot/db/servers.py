from pianobot.db import Connection


class Server:
    def __init__(
        self, server_id: int, prefix: str, channel: int, role: int, time: int, ping: int, rank: int
    ) -> None:
        self._server_id = server_id
        self._prefix = prefix
        self._channel = channel
        self._role = role
        self._time = time
        self._ping = ping
        self._rank = rank

    @property
    def server_id(self) -> int:
        return self._server_id

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def channel(self) -> int:
        return self._channel

    @property
    def role(self) -> int:
        return self._role

    @property
    def time(self) -> int:
        return self._time

    @property
    def ping(self) -> int:
        return self._ping

    @property
    def rank(self) -> int:
        return self._rank


class ServerTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    async def get_all(self) -> list[Server]:
        result = await self._con.query('SELECT * FROM servers')
        return [Server(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in result]

    async def get(self, server_id: int) -> Server | None:
        result = await self._con.query('SELECT * FROM servers WHERE id = $1', server_id)
        if result:
            row = result[0]
            return Server(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        return None

    async def add(self, server_id: int) -> None:
        await self._con.execute('INSERT INTO servers (id) VALUES ($1)', server_id)

    async def update_channel(self, server_id: int, channel: int) -> None:
        await self._con.execute(
            'UPDATE servers SET channel = $1 WHERE id = $2', channel, server_id
        )

    async def update_prefix(self, server_id: int, prefix: str) -> None:
        await self._con.execute('UPDATE servers SET prefix = $1 WHERE id = $2', prefix, server_id)

    async def update_ping(self, server_id: int, ping: int) -> None:
        await self._con.execute('UPDATE servers SET ping = $1 WHERE id = $2', ping, server_id)

    async def update_rank(self, server_id: int, rank: int) -> None:
        await self._con.execute('UPDATE servers SET rank = $1 WHERE id = $2', rank, server_id)

    async def update_role(self, server_id: int, role: int) -> None:
        await self._con.execute('UPDATE servers SET role = $1 WHERE id = $2', role, server_id)

    async def update_time(self, server_id: int, time: float) -> None:
        await self._con.execute('UPDATE servers SET time = $1 WHERE id = $2', time, server_id)

    async def remove(self, server_id: int) -> None:
        await self._con.execute('DELETE FROM servers WHERE id = $1', server_id)
