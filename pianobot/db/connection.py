from logging import getLogger

import psycopg2

class Connection:
    def __init__(
        self,
        database: str,
        host: str,
        password: str,
        user: str
    ):
        self._database = database
        self._host = host
        self._password = password
        self._user = user
        self._con = psycopg2.connect(
            database=database,
            host=host,
            password=password,
            user=user
        )
        self._con.autocommit = True
        getLogger('database').debug('Connected to database %s', self._database)

    def disconnect(self):
        self.con.close()
        getLogger('database').debug('Disconnected from database %s', self._database)

    def query(self, sql: str, *args) -> tuple:
        if self._con.closed != 0:
            self.__init__(self._database, self._host, self._password, self._user)
        cursor = self._con.cursor()
        cursor.execute(sql, args)
        self._con.commit()
        try:
            rows = cursor.fetchall()
        except psycopg2.ProgrammingError:
            rows = ()
        cursor.close()
        return rows
