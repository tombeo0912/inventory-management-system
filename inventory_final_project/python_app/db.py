"""
Database connection helper for the Inventory Management System CLI.
Default database name is `Personal_Finance` to match the user's environment.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

import mysql.connector
from mysql.connector.connection import MySQLConnection


DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "1234"),
    "database": os.getenv("MYSQL_DATABASE", "Personal_Finance"),
}


def get_connection() -> MySQLConnection:
    return mysql.connector.connect(**DB_CONFIG)


@contextmanager
def get_cursor(dictionary: bool = True) -> Generator:
    conn = get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield conn, cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
