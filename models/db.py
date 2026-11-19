from contextlib import contextmanager

import mysql.connector

from config import connection_options

@contextmanager
def connection():
    db = mysql.connector.connect(**connection_options())
    try:
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()

def query(sql, params=()):
    with connection() as db, db.cursor(dictionary=True) as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()

def execute(sql, params=()):
    with connection() as db, db.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.lastrowid
