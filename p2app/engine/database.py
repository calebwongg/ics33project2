import sqlite3
from pathlib import Path


def open_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute('PRAGMA foreign_keys = ON;')
    return connection


def close_database(connection: sqlite3.Connection) -> None:
    connection.close()