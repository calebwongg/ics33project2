import sqlite3
from pathlib import Path


def open_database(path: Path) -> sqlite3.Connection:
    """opens the sqlite database at the given path and turns on foreign key checks"""
    connection = sqlite3.connect(path)
    connection.execute('PRAGMA foreign_keys = ON;')
    return connection


def close_database(connection: sqlite3.Connection) -> None:
    """closes the given database connection"""
    connection.close()