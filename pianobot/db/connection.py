from logging import getLogger
from typing import Any

import psycopg2


class Connection:
    def __init__(self, database: str, host: str, password: str, user: str) -> None:
        self._database = database
        self._host = host
        self._password = password
        self._user = user
        self._con = self.connect()

    def connect(self):
        con = psycopg2.connect(
            database=self._database,
            host=self._host,
            password=self._password,
            user=self._user,
        )
        con.autocommit = True
        getLogger('database').debug('Connected to database %s', self._database)
        return con

    def disconnect(self) -> None:
        self._con.close()
        getLogger('database').debug('Disconnected from database %s', self._database)

    def query(self, sql: str, *args: Any) -> list[tuple[Any, ...]]:
        if self._con.closed != 0:
            self._con = self.connect()
        cursor = self._con.cursor()
        cursor.execute(sql, args)
        self._con.commit()
        try:
            rows: list[tuple[Any, ...]] = cursor.fetchall()
        except psycopg2.ProgrammingError:
            rows = []
        cursor.close()
        return rows
