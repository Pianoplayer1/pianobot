from datetime import datetime

from pianobot.db import Connection


class Server:
    def __init__(
        self,
        server_id: int,
        prefix: str,
        territory_log_channel: int | None,
        ping_role: int | None,
        last_ping: datetime | None,
        ping_interval: int | None,
        ping_rank: int | None,
    ) -> None:
        self._server_id = server_id
        self._prefix = prefix
        self._territory_log_channel = territory_log_channel
        self._ping_role = ping_role
        self._last_ping = last_ping
        self._ping_interval = ping_interval
        self._ping_rank = ping_rank

    @property
    def server_id(self) -> int:
        return self._server_id

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def territory_log_channel(self) -> int | None:
        return self._territory_log_channel

    @property
    def ping_role(self) -> int | None:
        return self._ping_role

    @property
    def last_ping(self) -> datetime | None:
        return self._last_ping

    @property
    def ping_interval(self) -> int | None:
        return self._ping_interval

    @property
    def ping_rank(self) -> int | None:
        return self._ping_rank


class ServerTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    async def add(self, server_id: int) -> None:
        await self._con.execute('INSERT INTO servers (id) VALUES ($1)', server_id)

    async def get_all(self) -> list[Server]:
        result = await self._con.query('SELECT * FROM servers')
        return [Server(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in result]

    async def get(self, server_id: int) -> Server | None:
        result = await self._con.query('SELECT * FROM servers WHERE id = $1', server_id)
        if result:
            row = result[0]
            return Server(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        return None

    async def update_prefix(self, server_id: int, prefix: str) -> None:
        await self._con.execute('UPDATE servers SET prefix = $1 WHERE id = $2', prefix, server_id)

    async def update_territory_log_channel(self, server_id: int, channel: int | None) -> None:
        await self._con.execute(
            'UPDATE servers SET territory_log_channel = $1 WHERE id = $2', channel, server_id
        )

    async def update_ping_role(self, server_id: int, ping_role: int | None) -> None:
        await self._con.execute(
            'UPDATE servers SET ping_role = $1 WHERE id = $2', ping_role, server_id
        )

    async def update_last_ping(self, server_id: int, last_ping: datetime | None) -> None:
        await self._con.execute(
            'UPDATE servers SET last_ping = $1 WHERE id = $2', last_ping, server_id
        )

    async def update_ping_interval(self, server_id: int, ping_interval: int | None) -> None:
        await self._con.execute(
            'UPDATE servers SET ping_interval = $1 WHERE id = $2', ping_interval, server_id
        )

    async def update_ping_rank(self, server_id: int, ping_rank: int | None) -> None:
        await self._con.execute(
            'UPDATE servers SET ping_rank = $1 WHERE id = $2', ping_rank, server_id
        )

    async def remove(self, server_id: int) -> None:
        await self._con.execute('DELETE FROM servers WHERE id = $1', server_id)
