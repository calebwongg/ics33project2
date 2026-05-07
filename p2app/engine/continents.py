import sqlite3
from p2app.events.continents import Continent, ContinentSearchResultEvent
from p2app.events.app import ErrorEvent
from p2app.events.continents import (
    Continent, ContinentSearchResultEvent, ContinentLoadedEvent,
    ContinentSavedEvent, SaveContinentFailedEvent
)


def search_continents(connection: sqlite3.Connection,
                      continent_code: str, name: str):
    """searches the continent table by code and/or name and yields one result event per match"""
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
    """loads one continent by its id and yields a loaded event or an error event if not found"""
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
    """inserts a new continent and yields the saved event or a failed event on error"""
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

def save_continent(connection: sqlite3.Connection, continent: Continent):
    """updates an existing continent and yields the saved event or a failed event on error"""
    try:
        connection.execute(
            'UPDATE continent SET continent_code = ?, name = ? WHERE continent_id = ?',
            (continent.continent_code, continent.name, continent.continent_id)
        )
        connection.commit()
        yield ContinentSavedEvent(continent)
    except sqlite3.Error as e:
        connection.rollback()
        yield SaveContinentFailedEvent(str(e))