from typing import Union

from .connection import Connection

class Server:
    def __init__(self, id, prefix, channel, role, time, ping):
        self._id = id
        self._prefix = prefix
        self._channel = channel
        self._role = role
        self._time = time
        self._ping = ping

    @property
    def id(self) -> int:
        return self._id

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

class Manager:
    def __init__(self, db: Connection):
        self._db = db

    def get_all(self) -> list[Server]:
        result = self._db.query('SELECT * FROM servers;')
        return [Server(row[0], row[1], row[2], row[3], row[4], row[5]) for row in result]
    
    def get(self, id: int) -> Union[Server, None]:
        result = self._db.query('SELECT * FROM servers WHERE id = %s;', id)
        if result:
            row = result[0]
            return Server(row[0], row[1], row[2], row[3], row[4], row[5])
        else:
            return None

    def add(self, id: int):
        self._db.query('INSERT INTO servers (id) VALUES (%s);', id)
    
    def update_prefix(self, id: int, prefix: str):
        self._db.query('UPDATE servers SET prefix = %s WHERE id = %s;', prefix, id)

    def update_time(self, id: int, time: int):
        self._db.query('UPDATE servers SET time = %s WHERE id = %s;', time, id)
    
    def remove(self, id: int):
        self._db.query('DELETE FROM servers WHERE id = %s;', id)
