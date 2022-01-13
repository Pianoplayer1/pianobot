from logging import getLogger
from os import getenv

import psycopg2

class Connection:
    def __init__(self):
        self.con = psycopg2.connect(
            database = getenv('PG_DB'),
            host = getenv('PG_HOST'),
            password = getenv('PG_PASS'),
            user = getenv('PG_USER')
        )
        self.con.autocommit = True
        getLogger('database').debug('Connected to database')

    def disconnect(self):
        self.con.close()
        getLogger('database').debug('Disconnected from database')

    def query(self, sql: str, *args) -> tuple:
        if self.con.closed != 0:
            self.__init__()
        cursor = self.con.cursor()
        cursor.execute(sql, args)
        self.con.commit()
        try:
            rows = cursor.fetchall()
        except psycopg2.ProgrammingError:
            rows = ()
        cursor.close()
        return rows
