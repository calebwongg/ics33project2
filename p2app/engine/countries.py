# p2app/engine/countries.py
#
# ICS 33 Spring 2026
# Project 2: Learning to Fly
#
# Functions that handle country-related database operations.

import sqlite3
from p2app.events.countries import (
    Country, CountrySearchResultEvent, CountryLoadedEvent
)
from p2app.events.app import ErrorEvent


def _empty_to_none(value: str) -> str | None:
    if value is None or value == '':
        return None
    return value


def search_countries(connection: sqlite3.Connection,
                     country_code: str, name: str):
    query = ('SELECT country_id, country_code, name, continent_id, '
             'wikipedia_link, keywords FROM country WHERE 1 = 1')
    params = []

    if country_code is not None and country_code != '':
        query += ' AND country_code = ?'
        params.append(country_code)

    if name is not None and name != '':
        query += ' AND name = ?'
        params.append(name)

    cursor = connection.execute(query, params)

    for row in cursor:
        country = Country(
            country_id=row[0],
            country_code=row[1],
            name=row[2],
            continent_id=row[3],
            wikipedia_link=row[4],
            keywords=row[5]
        )
        yield CountrySearchResultEvent(country)


def load_country(connection: sqlite3.Connection, country_id: int):
    """Loads a single country by its ID.
    Yields a CountryLoadedEvent or an ErrorEvent."""
    cursor = connection.execute(
        'SELECT country_id, country_code, name, continent_id, '
        'wikipedia_link, keywords FROM country WHERE country_id = ?',
        (country_id,)
    )
    row = cursor.fetchone()

    if row is not None:
        country = Country(
            country_id=row[0],
            country_code=row[1],
            name=row[2],
            continent_id=row[3],
            wikipedia_link=row[4],
            keywords=row[5]
        )
        yield CountryLoadedEvent(country)
    else:
        yield ErrorEvent('Country not found.')