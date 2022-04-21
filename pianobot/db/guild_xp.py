from datetime import datetime
from logging import getLogger
from typing import Any

from psycopg2.errors import UniqueViolation

from pianobot.db import Connection
from pianobot.utils import get_rounded_time


class GuildXP:
    def __init__(self, time: datetime, data: dict[str, int]) -> None:
        self._time = time
        self._data = data

    @property
    def time(self) -> datetime:
        return self._time

    @property
    def data(self) -> dict[str, int]:
        return self._data


class GuildXPTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    def get_members(self) -> list[str]:
        result = self._con.query(
            'SELECT column_name FROM information_schema.columns WHERE table_name = \'guildXP\''
        )
        return [] if len(result) <= 1 else [column[0] for column in result[1:]]

    def get(self, time: datetime) -> GuildXP | None:
        return self._bind(self._con.query('SELECT * FROM "guildXP" WHERE time = %s', time))

    def get_first(self, interval: str) -> GuildXP | None:
        return self._bind(
            self._con.query(
                f'SELECT * FROM "guildXP" WHERE time > (CURRENT_TIMESTAMP - {interval}::interval)'
                ' ORDER BY time LIMIT 1'
            )
        )

    def _bind(self, result: list[tuple[Any, ...]]) -> GuildXP | None:
        members = self.get_members()
        if len(result) > 0:
            row = result[0]
            data = {members[i]: row[i + 1] for i in range(len(members))}
            return GuildXP(row[0], data)
        return None

    def get_last(self, amount: int = 1) -> list[GuildXP]:
        result = self._con.query(f'SELECT * FROM "guildXP" ORDER BY time DESC LIMIT {amount}')
        members = self.get_members()
        return [GuildXP(row[0], dict(zip(members, row[1:]))) for row in result]

    def update_columns(self, names: list[str]) -> None:
        columns = self.get_members()
        to_add = set(names)
        to_add.difference_update(columns)
        add_string = ', '.join(f'ADD COLUMN "{name}" BIGINT DEFAULT 0 NOT NULL' for name in to_add)
        to_remove = set(columns)
        to_remove.difference_update(names)
        remove_string = ', '.join([f'DROP COLUMN IF EXISTS "{name}"' for name in to_remove])

        if add_string and remove_string:
            remove_string = ', ' + remove_string
        if add_string or remove_string:
            self._con.query(f'ALTER TABLE "guildXP" {add_string}{remove_string};')

    def add(self, data: dict[str, int]) -> None:
        rounded_time = get_rounded_time(minutes=5)

        columns = ', '.join(f'"{key}"' for key in data)
        placeholders = ', '.join('%s' for _ in data)

        try:
            self._con.query(
                f'INSERT INTO "guildXP"(time, {columns}) VALUES (%s, {placeholders})',
                rounded_time,
                *data.values(),
            )
        except UniqueViolation:
            getLogger('database').debug('Duplicate guild xp time')

    def cleanup(self) -> None:
        self._con.query(
            'DELETE FROM "guildXP" WHERE time < (CURRENT_TIMESTAMP - \'7 DAY\'::interval) AND'
            ' to_char(time, \'MI\') != \'00\''
        )
        self._con.query(
            'DELETE FROM "guildXP" WHERE time < (CURRENT_TIMESTAMP - \'14 DAY\'::interval) AND'
            ' to_char(time, \'HH24:MI\') != \'00:00\''
        )
