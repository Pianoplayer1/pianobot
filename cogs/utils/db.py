from os import getenv
import logging
import psycopg2

def connect():
    con = psycopg2.connect(host = getenv('PG_HOST'), user = getenv('PG_USER'), password = getenv('PG_PASS'), database = getenv('PG_DB'))
    con.autocommit = True
    logging.getLogger('database').debug('Connected to database')
    return con

def disconnect(con):
    con.close()
    logging.getLogger('database').debug('Disconnected from database')

def query(con, sql : str, vals : tuple) -> tuple:
    if type(vals) != tuple: vals = (vals,)
    sql = sql.replace('`', '"')
    cursor = con.cursor()
    cursor.execute(sql, vals)
    con.commit()
    try:
        rows = cursor.fetchall()
    except psycopg2.ProgrammingError:
        rows = ()
    cursor.close()
    return rows