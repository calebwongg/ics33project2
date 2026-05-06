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
from p2app.engine.database import open_database, close_database
from p2app.events.continents import StartContinentSearchEvent
from p2app.engine.continents import search_continents


class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        self._connection = None

    def process_event(self, event):
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

    def _open_database(self, event):
        try:
            self._connection = open_database(event.path())
            yield DatabaseOpenedEvent(event.path())
        except Exception as e:
            yield DatabaseOpenFailedEvent(str(e))

    def _close_database(self):
        if self._connection is not None:
            close_database(self._connection)
            self._connection = None
        yield DatabaseClosedEvent()