from datetime import datetime, timedelta
from logging import getLogger
from psycopg2.errors import UniqueViolation
from typing import Union

from .connection import Connection

class GuildXP:
    def __init__(self, time, data):
        self._time = time
        self._data = data

    @property
    def time(self) -> datetime:
        return self._time

    @property
    def data(self) -> dict[str: int]:
        return self._data

class Manager:
    def __init__(self, db: Connection):
        self._db = db

    def get_members(self) -> list[str]:
        result = self._db.query('SELECT column_name FROM information_schema.columns WHERE table_name = \'guildXP\';')
        if len(result) <= 1:
            return []
        return [column[0] for column in result[1:]]

    def get(self, time: datetime) -> Union[GuildXP, None]:
        result = self._db.query('SELECT * FROM "guildXP" WHERE time = %s;', time)
        members = self.get_members()
        if result:
            row = result[0]
            data = {members[i]: row[i + 1] for i in range(len(members))}
            return GuildXP(row[0], data)
        else:
            return None
    
    def get_first(self, interval: str) -> Union[GuildXP, None]:
        result = self._db.query(f'SELECT * FROM "guildXP" WHERE time > (CURRENT_TIMESTAMP - \'{interval}\'::interval) ORDER BY time ASC LIMIT 1;')
        members = self.get_members()
        if result:
            row = result[0]
            data = {members[i]: row[i + 1] for i in range(len(members))}
            return GuildXP(row[0], data)
        else:
            return None
    
    def get_last(self, amount: int = 1) -> list[GuildXP]:
        result = self._db.query(f'SELECT * FROM "guildXP" ORDER BY time DESC LIMIT {amount};')
        members = self.get_members()
        return [GuildXP(row[0], {name: row[i + 1] for i, name in enumerate(members)}) for row in result]

    def update_columns(self, names: list[str]):
        columns = self.get_members()
        to_add = set(names)
        to_add.difference_update(columns)
        add_string = ', '.join([f'ADD COLUMN "{name}" BIGINT DEFAULT 0 NOT NULL' for name in to_add])
        to_remove = set(columns)
        to_remove.difference_update(names)
        remove_string = ', '.join([f'DROP COLUMN IF EXISTS "{name}"' for name in to_remove])

        if add_string and remove_string:
            remove_string = ', ' + remove_string
        if add_string or remove_string:
            self._db.query(f'ALTER TABLE "guildXP" {add_string}{remove_string};')

    def add(self, data: dict[str: int]):
        time = datetime.utcnow()
        interval = 300
        seconds = (time.replace(tzinfo = None) - time.min).seconds
        difference = (seconds + interval / 2) // interval * interval - seconds
        rounded_time = str(time + timedelta(0, difference, -time.microsecond))

        columns = '", "'.join(data.keys())
        placeholders = '%s' + ', %s' * len(data)
        sql = f'INSERT INTO "guildXP"(time, "{columns}") VALUES ({placeholders});'
        
        try:
            self._db.query(sql, rounded_time, *data.values())
        except UniqueViolation:
            getLogger('database').debug('Duplicate guild xp time')

    def cleanup(self):
        self._db.query('DELETE FROM "guildXP" WHERE time < (CURRENT_TIMESTAMP - \'7 DAY\'::interval) AND to_char(time, \'MI\') != \'00\'')
        self._db.query('DELETE FROM "guildXP" WHERE time < (CURRENT_TIMESTAMP - \'14 DAY\'::interval) AND to_char(time, \'HH24:MI\') != \'00:00\'')
