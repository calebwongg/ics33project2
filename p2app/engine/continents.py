import sqlite3
from p2app.events.continents import Continent, ContinentSearchResultEvent
from p2app.events.app import ErrorEvent
from p2app.events.continents import (
    Continent, ContinentSearchResultEvent, ContinentLoadedEvent,
    ContinentSavedEvent, SaveContinentFailedEvent
)


def search_continents(connection: sqlite3.Connection,
                      continent_code: str, name: str):
    """Searches for continents matching the given code and/or name.
    Yields a ContinentSearchResultEvent for each match found."""
    query = 'SELECT continent_id, continent_code, name FROM continent WHERE 1 = 1'
    params = []

    if continent_code is not None and continent_code != '':
        query += ' AND continent_code = ?'
        params.append(continent_code)

    if name is not None and name != '':
        query += ' AND name = ?'
        params.append(name)

    cursor = connection.execute(query, params)

    for row in cursor:
        continent = Continent(
            continent_id=row[0],
            continent_code=row[1],
            name=row[2]
        )
        yield ContinentSearchResultEvent(continent)

def load_continent(connection: sqlite3.Connection, continent_id: int):
    cursor = connection.execute(
        'SELECT continent_id, continent_code, name FROM continent WHERE continent_id = ?',
        (continent_id,)
    )
    row = cursor.fetchone()

    if row is not None:
        continent = Continent(
            continent_id=row[0],
            continent_code=row[1],
            name=row[2]
        )
        yield ContinentLoadedEvent(continent)
    else:
        yield ErrorEvent('Continent not found.')


def save_new_continent(connection: sqlite3.Connection, continent: Continent):
    try:
        cursor = connection.execute(
            'INSERT INTO continent (continent_code, name) VALUES (?, ?)',
            (continent.continent_code, continent.name)
        )
        connection.commit()

        new_continent = Continent(
            continent_id=cursor.lastrowid,
            continent_code=continent.continent_code,
            name=continent.name
        )
        yield ContinentSavedEvent(new_continent)
    except sqlite3.Error as e:
        connection.rollback()
        yield SaveContinentFailedEvent(str(e))