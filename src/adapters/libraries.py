from dataclasses import dataclass
from typing import Any, ContextManager

import geopy
from ferrea.clients.db import DBClient
from ferrea.core.context import Context
from ferrea.observability.logs import ferrea_logger
from neo4j.spatial import Point

from models.exceptions import FerreaLibraryNotCreated
from models.library import Library


@dataclass
class LibrariesRepository:
    """Repository class for interacting with the DB for the Libraries entities.

    Returns:
        _type_: the repository class.
    """

    db_client: ContextManager[DBClient]
    context: Context

    def _build_library(self, raw_library: dict[str, Any]) -> Library:
        """Helper method to build a serialized version."""
        try:
            ferrea_logger.debug(
                f"Retrieved library: {raw_library['name']}",
                **self.context.log,
            )
        except KeyError as e:
            ferrea_logger.error(e)
            ferrea_logger.debug(f"{self.context.log}")
            ferrea_logger.debug(f"Retrieved library: {raw_library=}")

        point: Point = raw_library["location"]
        raw_library["longitude"] = point.x
        raw_library["latitude"] = point.y

        return Library(**raw_library)

    def find_all_libraries(self) -> list[Library]:
        """
        This method gets all libraries on the db.

        Returns:
            list[Library]: the list of all Libraries.
        """
        query = "MATCH (l:Library) return l"

        with self.db_client as session:
            libraries_raw = session.read(query=query)

        libraries = list()
        for library in libraries_raw:
            temp = dict(library[0].items())
            libraries.append(self._build_library(temp))

        return libraries

    def find_a_library(self, name: str) -> Library | None:
        """
        This method search for the desired library on the db.

        Args:
            name (str): the name of the library.

        Returns:
            Library | None: the library if found, else None.
        """
        query = "MATCH (l:Library) WHERE l.name = $library_name RETURN l"
        params: dict[str, str | int | float] = {"library_name": name}

        with self.db_client as session:
            library_raw = session.read(query, params)

        if len(library_raw) == 0:
            return

        temp = dict(library_raw[0][0].items())
        return self._build_library(temp)

    def create_library(self, data: Library) -> Library:
        """
        This method creates a library on the db.

        Args:
            data (Library): the data of the library to create.

        Returns:
            Library: the created library.
        """
        geolocator = geopy.Nominatim(user_agent="my_geo_coder")
        location = self._find_location(data.address, geolocator)

        query = (
            "MERGE (l:Library {name: $name, phone: $phone, address: $address, email: $email, "
            "location: point({latitude: $latitude, longitude: $longitude}), fid: randomUUID()})"
        )
        params = {
            "name": data.name,
            "phone": data.phone,
            "address": data.address,
            "email": data.email,
        }
        if location is not None:
            params["latitude"] = location.latitude
            params["longitude"] = location.longitude

        with self.db_client as session:
            session.write(query, params)

        created_library = self.find_a_library(data.name)
        if created_library is None:
            raise FerreaLibraryNotCreated(
                f"Unable to find {data.name} library after its creation."
            )

        return created_library

    def _find_location(
        self, address: str, geolocator: geopy.Nominatim
    ) -> geopy.Location | None:
        location = geolocator.geocode(address)

        return location  # type: ignore
