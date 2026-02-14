"""
Database Helper - Abstraction layer for MySQL/Postgres compatibility
"""
from database import get_db_connection, db_config
import psycopg2.extras

def is_postgres():
    """Check if we're using Postgres"""
    return "pg.koyeb.app" in db_config.get("host", "")

def get_cursor(conn, dict_cursor=False):
    """Get a cursor with optional dictionary mode"""
    if is_postgres():
        if dict_cursor:
            return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return conn.cursor()
    else:
        if dict_cursor:
            return conn.cursor(dictionary=True)
        return conn.cursor()

def execute_insert(cursor, sql, params):
    """Execute INSERT and return last inserted ID"""
    if is_postgres():
        # Postgres: Use RETURNING
        sql_with_returning = sql + " RETURNING id"
        cursor.execute(sql_with_returning, params)
        return cursor.fetchone()[0]
    else:
        # MySQL: Use lastrowid
        cursor.execute(sql, params)
        return cursor.lastrowid
