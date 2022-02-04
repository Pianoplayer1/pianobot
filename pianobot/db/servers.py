from pianobot.db import Connection

class Server:
    def __init__(self, server_id, prefix, channel, role, time, ping, rank):
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
    def __init__(self, con: Connection):
        self._con = con

    def get_all(self) -> list[Server]:
        result = self._con.query('SELECT * FROM servers;')
        return [Server(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in result]

    def get(self, server_id: int) -> Server | None:
        result = self._con.query('SELECT * FROM servers WHERE id = %s;', server_id)
        if result:
            row = result[0]
            return Server(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        return None

    def add(self, server_id: int):
        self._con.query('INSERT INTO servers (id) VALUES (%s);', server_id)

    def update_channel(self, server_id: int, channel: int):
        self._con.query('UPDATE servers SET channel = %s WHERE id = %s;', channel, server_id)

    def update_prefix(self, server_id: int, prefix: str):
        self._con.query('UPDATE servers SET prefix = %s WHERE id = %s;', prefix, server_id)

    def update_ping(self, server_id: int, ping: int):
        self._con.query('UPDATE servers SET ping = %s WHERE id = %s;', ping, server_id)

    def update_rank(self, server_id: int, rank: int):
        self._con.query('UPDATE servers SET rank = %s WHERE id = %s;', rank, server_id)

    def update_role(self, server_id: int, role: int):
        self._con.query('UPDATE servers SET role = %s WHERE id = %s;', role, server_id)

    def update_time(self, server_id: int, time: int):
        self._con.query('UPDATE servers SET time = %s WHERE id = %s;', time, server_id)

    def remove(self, server_id: int):
        self._con.query('DELETE FROM servers WHERE id = %s;', server_id)
