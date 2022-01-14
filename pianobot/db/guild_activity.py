from datetime import datetime
from logging import getLogger

from psycopg2.errors import UniqueViolation

from pianobot.db import Connection
from pianobot.utils.time import get_rounded_time

class GuildActivityTable:
    def __init__(self, con: Connection):
        self._con = con

    def get(self, guild: str, interval: int) -> dict[datetime: int]:
        return dict(self._con.query(
            f'SELECT time, "{guild}" FROM "guildActivity" WHERE time > '
            f'(CURRENT_TIMESTAMP - \'{interval} day\'::interval) ORDER BY time ASC;'
        ))

    def add(self, data: dict[str: int]):
        columns = '", "'.join(data.keys())
        placeholders = '%s' + ', %s' * len(data)

        try:
            self._con.query(
                f'INSERT INTO "guildActivity" (time, "{columns}") VALUES ({placeholders});',
                get_rounded_time(minutes = 5),
                *data.values()
            )
        except UniqueViolation:
            getLogger('database').debug('Duplicate guild activity time')

    def cleanup(self):
        self._con.query(
            'DELETE FROM "guildActivity" WHERE time < (CURRENT_TIMESTAMP - \'7 DAY\'::interval) '
            'AND to_char(time, \'MI\') != \'00\''
        )
        self._con.query(
            'DELETE FROM "guildActivity" WHERE time < (CURRENT_TIMESTAMP - \'14 DAY\'::interval) '
            'AND to_char(time, \'HH24:MI\') != \'00:00\''
        )
