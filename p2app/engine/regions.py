# p2app/engine/regions.py
#
# ICS 33 Spring 2026
# Project 2: Learning to Fly
#
# Functions that handle region-related database operations.

import sqlite3
from p2app.events.app import ErrorEvent
from p2app.events.regions import (
    Region, RegionSearchResultEvent, RegionLoadedEvent,
    RegionSavedEvent, SaveRegionFailedEvent
)


def _empty_to_none(value: str) -> str | None:
    """Converts empty strings to None for nullable TEXT columns."""
    if value is None or value == '':
        return None
    return value

def search_regions(connection: sqlite3.Connection,
                   region_code: str, local_code: str, name: str):
    """Searches for regions matching the given code, local code, and/or name.
    Yields a RegionSearchResultEvent for each match found."""
    query = ('SELECT region_id, region_code, local_code, name, '
             'continent_id, country_id, wikipedia_link, keywords '
             'FROM region WHERE 1 = 1')
    params = []

    if region_code is not None and region_code != '':
        query += ' AND region_code = ?'
        params.append(region_code)

    if local_code is not None and local_code != '':
        query += ' AND local_code = ?'
        params.append(local_code)

    if name is not None and name != '':
        query += ' AND name = ?'
        params.append(name)

    cursor = connection.execute(query, params)

    for row in cursor:
        region = Region(
            region_id=row[0],
            region_code=row[1],
            local_code=row[2],
            name=row[3],
            continent_id=row[4],
            country_id=row[5],
            wikipedia_link=row[6],
            keywords=row[7]
        )
        yield RegionSearchResultEvent(region)


def load_region(connection: sqlite3.Connection, region_id: int):
    """Loads a single region by its ID.
    Yields a RegionLoadedEvent or an ErrorEvent."""
    cursor = connection.execute(
        'SELECT region_id, region_code, local_code, name, '
        'continent_id, country_id, wikipedia_link, keywords '
        'FROM region WHERE region_id = ?',
        (region_id,)
    )
    row = cursor.fetchone()

    if row is not None:
        region = Region(
            region_id=row[0],
            region_code=row[1],
            local_code=row[2],
            name=row[3],
            continent_id=row[4],
            country_id=row[5],
            wikipedia_link=row[6],
            keywords=row[7]
        )
        yield RegionLoadedEvent(region)
    else:
        yield ErrorEvent('Region not found.')

def save_new_region(connection: sqlite3.Connection, region: Region):
    """Inserts a new region into the database.
    Yields a RegionSavedEvent on success or SaveRegionFailedEvent on failure."""
    try:
        wikipedia_link = _empty_to_none(region.wikipedia_link)
        keywords = _empty_to_none(region.keywords)

        cursor = connection.execute(
            'INSERT INTO region (region_code, local_code, name, '
            'continent_id, country_id, wikipedia_link, keywords) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (region.region_code, region.local_code, region.name,
             region.continent_id, region.country_id,
             wikipedia_link, keywords)
        )
        connection.commit()

        new_region = Region(
            region_id=cursor.lastrowid,
            region_code=region.region_code,
            local_code=region.local_code,
            name=region.name,
            continent_id=region.continent_id,
            country_id=region.country_id,
            wikipedia_link=wikipedia_link,
            keywords=keywords
        )
        yield RegionSavedEvent(new_region)
    except sqlite3.Error as e:
        connection.rollback()
        yield SaveRegionFailedEvent(str(e))


def save_region(connection: sqlite3.Connection, region: Region):
    """Updates an existing region in the database.
    Yields a RegionSavedEvent on success or SaveRegionFailedEvent on failure."""
    try:
        wikipedia_link = _empty_to_none(region.wikipedia_link)
        keywords = _empty_to_none(region.keywords)

        connection.execute(
            'UPDATE region SET region_code = ?, local_code = ?, name = ?, '
            'continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? '
            'WHERE region_id = ?',
            (region.region_code, region.local_code, region.name,
             region.continent_id, region.country_id,
             wikipedia_link, keywords, region.region_id)
        )
        connection.commit()

        updated_region = Region(
            region_id=region.region_id,
            region_code=region.region_code,
            local_code=region.local_code,
            name=region.name,
            continent_id=region.continent_id,
            country_id=region.country_id,
            wikipedia_link=wikipedia_link,
            keywords=keywords
        )
        yield RegionSavedEvent(updated_region)
    except sqlite3.Error as e:
        connection.rollback()
        yield SaveRegionFailedEvent(str(e))