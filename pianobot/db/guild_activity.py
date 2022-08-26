from datetime import datetime
from logging import getLogger

from asyncpg import UniqueViolationError

from pianobot.db import Connection
from pianobot.utils import get_rounded_time


class GuildActivityTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    async def get(self, guild: str, interval: str) -> dict[datetime, int]:
        guild = f'"{guild}"'
        result = await self._con.query(
            f'SELECT time, {guild} FROM guild_activity WHERE time > (CURRENT_TIMESTAMP -'
            f' \'{interval}\'::interval) AND {guild} IS NOT NULL ORDER BY time'
        )
        return {} if len(result) == 0 else {row[0]: row[1] for row in result}

    async def update_columns(self, guilds: list[str]) -> None:
        result = await self._con.query(
            'SELECT column_name FROM information_schema.columns WHERE table_name ='
            ' \'guild_activity\''
        )
        current_guilds = [] if len(result) <= 1 else [column[0] for column in result[1:]]
        to_add = set(guilds).difference(current_guilds)
        add_string = ', '.join(f'ADD COLUMN "{name}" INTEGER' for name in to_add)
        to_remove = set(current_guilds).difference(guilds)
        remove_string = ', '.join([f'DROP COLUMN IF EXISTS "{name}"' for name in to_remove])

        if add_string and remove_string:
            remove_string = ', ' + remove_string
        if add_string or remove_string:
            await self._con.execute(f'ALTER TABLE guild_activity {add_string}{remove_string};')

    async def add(self, data: dict[str, int | None]) -> None:
        rounded_time = get_rounded_time(minutes=5)

        columns = ', '.join(f'"{key}"' for key in data)
        placeholders = ', '.join(f'${i + 2}' for i in range(len(data)))

        try:
            await self._con.execute(
                f'INSERT INTO guild_activity (time, {columns}) VALUES ($1, {placeholders})',
                rounded_time,
                *data.values(),
            )
        except UniqueViolationError:
            getLogger('database').debug('Duplicate guild activity time')

    async def cleanup(self) -> None:
        await self._con.execute(
            'DELETE FROM guild_activity WHERE time < (CURRENT_TIMESTAMP - \'7 DAY\'::interval)'
            ' AND to_char(time, \'MI\') != \'00\''
        )
        await self._con.execute(
            'DELETE FROM guild_activity WHERE time < (CURRENT_TIMESTAMP - \'14 DAY\'::interval)'
            ' AND to_char(time, \'HH24:MI\') != \'00:00\''
        )
