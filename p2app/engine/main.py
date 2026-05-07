# p2app/engine/main.py
#
# ICS 33 Spring 2026
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.

from p2app.events.app import QuitInitiatedEvent, EndApplicationEvent
from p2app.events.database import (
    OpenDatabaseEvent, CloseDatabaseEvent,
    DatabaseOpenedEvent, DatabaseOpenFailedEvent, DatabaseClosedEvent
)
from p2app.events.continents import (
    StartContinentSearchEvent, LoadContinentEvent,
    SaveNewContinentEvent, SaveContinentEvent
)
from p2app.events.countries import (
    StartCountrySearchEvent, LoadCountryEvent,
    SaveNewCountryEvent, SaveCountryEvent
)
from p2app.events.regions import (
    StartRegionSearchEvent, LoadRegionEvent,
    SaveNewRegionEvent, SaveRegionEvent
)

from p2app.engine.database import open_database, close_database
from p2app.engine.continents import (
    search_continents, load_continent, save_new_continent, save_continent
)
from p2app.engine.countries import (
    search_countries, load_country, save_new_country, save_country
)
from p2app.engine.regions import (
    search_regions, load_region, save_new_region, save_region
)


class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """sets up the engine with no database connection yet"""
        self._connection = None

    def process_event(self, event):
        """receives an event from the ui, dispatches it to the right handler, and yields back any result events"""
        if isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()

        elif isinstance(event, OpenDatabaseEvent):
            yield from self._open_database(event)

        elif isinstance(event, CloseDatabaseEvent):
            yield from self._close_database()

        elif isinstance(event, StartContinentSearchEvent):
            yield from search_continents(
                self._connection,
                event.continent_code(), event.name()
            )

        elif isinstance(event, LoadContinentEvent):
            yield from load_continent(
                self._connection, event.continent_id()
            )

        elif isinstance(event, SaveNewContinentEvent):
            yield from save_new_continent(
                self._connection, event.continent()
            )

        elif isinstance(event, SaveContinentEvent):
            yield from save_continent(
                self._connection, event.continent()
            )

        elif isinstance(event, StartCountrySearchEvent):
            yield from search_countries(
                self._connection,
                event.country_code(), event.name()
            )

        elif isinstance(event, LoadCountryEvent):
            yield from load_country(
                self._connection, event.country_id()
            )

        elif isinstance(event, SaveNewCountryEvent):
            yield from save_new_country(
                self._connection, event.country()
            )

        elif isinstance(event, SaveCountryEvent):
            yield from save_country(
                self._connection, event.country()
            )

        elif isinstance(event, StartRegionSearchEvent):
            yield from search_regions(
                self._connection,
                event.region_code(), event.local_code(), event.name()
            )

        elif isinstance(event, LoadRegionEvent):
            yield from load_region(
                self._connection, event.region_id()
            )

        elif isinstance(event, SaveNewRegionEvent):
            yield from save_new_region(
                self._connection, event.region()
            )

        elif isinstance(event, SaveRegionEvent):
            yield from save_region(
                self._connection, event.region()
            )

    def _open_database(self, event):
        """opens the database at the path in the event and yields opened or open failed"""
        try:
            self._connection = open_database(event.path())
            yield DatabaseOpenedEvent(event.path())
        except Exception as e:
            self._connection = None
            yield DatabaseOpenFailedEvent(str(e))

    def _close_database(self):
        """closes the current connection if there is one and yields the closed event"""
        if self._connection is not None:
            close_database(self._connection)
            self._connection = None
        yield DatabaseClosedEvent()
