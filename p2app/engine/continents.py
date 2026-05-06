import sqlite3
from p2app.events.continents import Continent, ContinentSearchResultEvent


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