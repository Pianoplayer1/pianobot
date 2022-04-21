from datetime import datetime
from logging import getLogger

from psycopg2.errors import UniqueViolation

from pianobot.db import Connection
from pianobot.utils import get_rounded_time


class GuildActivityTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    def get(self, guild: str, interval: str) -> dict[datetime, int]:
        guild = f'"{guild}"'
        result = self._con.query(
            f'SELECT time, {guild} FROM "guildActivity" WHERE time > (CURRENT_TIMESTAMP -'
            f' {interval}::interval) AND {guild} IS NOT NULL ORDER BY time'
        )
        return {} if len(result) == 0 else {result[0][0]: result[0][1]}

    def add(self, data: dict[str, int | None]) -> None:
        rounded_time = get_rounded_time(minutes=5)

        columns = ', '.join(f'"{key}"' for key in data)
        placeholders = ', '.join('%s' for _ in data)

        try:
            self._con.query(
                f'INSERT INTO "guildActivity" (time, {columns}) VALUES (%s, {placeholders})',
                rounded_time,
                *data.values(),
            )
        except UniqueViolation:
            getLogger('database').debug('Duplicate guild activity time')

    def cleanup(self) -> None:
        self._con.query(
            'DELETE FROM "guildActivity" WHERE time < (CURRENT_TIMESTAMP - \'7 DAY\'::interval)'
            ' AND to_char(time, \'MI\') != \'00\''
        )
        self._con.query(
            'DELETE FROM "guildActivity" WHERE time < (CURRENT_TIMESTAMP - \'14 DAY\'::interval)'
            ' AND to_char(time, \'HH24:MI\') != \'00:00\''
        )
