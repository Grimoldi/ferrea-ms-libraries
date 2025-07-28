from dataclasses import dataclass
from typing import Any, ContextManager

import geopy
from ferrea.clients.db import DBClient
from ferrea.core.context import Context
from ferrea.observability.logs import ferrea_logger
from neo4j.spatial import Point

from models.exceptions import FerreaLibraryNotCreated, FerreaNonExistingLibrary
from models.library import Library

Neo4jParameter = dict[str, str | int | float]


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
        ferrea_logger.debug(
            f"Retrieved library: {raw_library['name']}, fid {raw_library['fid']}.",
            **self.context.log,
        )

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

    def find_a_library_by_fid(self, fid: str) -> Library:
        """
        This method search for the desired library on the db.

        Args:
            fid (str): the ferreaID of the object.

        Raises:
            FerreaNonExistingLibrary: if library is not found and operation cannot be carried on.

        Returns:
            Library: the found library.
        """
        query = "MATCH (l:Library) WHERE l.fid = $fid RETURN l"
        params: Neo4jParameter = {"fid": fid}

        with self.db_client as session:
            library_raw = session.read(query, params)

        if len(library_raw) == 0:
            ferrea_logger.warning(f"Unable to find library with fid {fid}.")
            raise FerreaNonExistingLibrary(
                f"Unable to find library based on the provided fid {fid}."
            )

        raw_result = dict(library_raw[0][0].items())
        return self._build_library(raw_result)

    def create_library(self, data: Library) -> Library:
        """
        This method creates a library on the db.

        Args:
            data (Library): the data of the library to create.

        Returns:
            Library: the created library.
        """
        params: Neo4jParameter = {
            "name": data.name,
            "phone": str(data.phone),
            "address": data.address,
            "email": str(data.email),
        }
        location = self._find_location(data.address)
        if location is not None:
            params["latitude"] = location.latitude
            params["longitude"] = location.longitude

        query = (
            "MERGE (l:Library {name: $name, phone: $phone, address: $address, email: $email, "
            "location: point({latitude: $latitude, longitude: $longitude}), fid: randomUUID()})"
            "RETURN l.fid"
        )

        with self.db_client as session:
            [[new_fid]] = session.write(query, params)

        created_library = self.find_a_library_by_fid(new_fid)
        if created_library is None:
            raise FerreaLibraryNotCreated(
                f"Unable to find {data.name} library after its creation."
            )

        return created_library

    def update_library(self, fid: str, new_value: Library) -> Library:
        """
        This method updates an existing library on the db, based on its fid (Ferrea ID).

        Args:
            fid (str): the ferreaID of the object.

        Raises:
            FerreaNonExistingLibrary: if library is not found and operation cannot be carried on.

        Returns:
            Library: the updated library.
        """
        # just check that the library exists, or raise an Error.
        _ = self.find_a_library_by_fid(fid)

        params: Neo4jParameter = {
            "name": new_value.name,
            "phone": str(new_value.phone),
            "address": new_value.address,
            "email": str(new_value.email),
        }
        location = self._find_location(new_value.address)
        if location is not None:
            params["latitude"] = location.latitude
            params["longitude"] = location.longitude

        query = (
            "MERGE (l:Library {name: $name, phone: $phone, address: $address, email: $email, "
            "location: point({latitude: $latitude, longitude: $longitude})})"
        )

        with self.db_client as session:
            session.write(query, params)

        return self.find_a_library_by_fid(fid)

    def delete_library(self, fid: str) -> Library:
        """
        This method deltes an existing library from the db, based on its fid (Ferrea ID).

        Args:
            fid (str): the ferreaID of the object.

        Raises:
            FerreaNonExistingLibrary: if library is not found and operation cannot be carried on.

        Returns:
            Library: the deleted library.
        """
        # just check that the library exists, or raise an Error.
        old_library = self.find_a_library_by_fid(fid)

        params: Neo4jParameter = {
            "fid": fid,
        }
        query = "MATCH (l:Library {fid: $fid}) DELETE l"

        with self.db_client as session:
            session.write(query, params)

        return old_library

    @property
    def _geolocator(self) -> geopy.Nominatim:
        """Integrated geolocator for geopy"""
        return geopy.Nominatim(user_agent="my_geo_coder")

    def _find_location(self, address: str) -> geopy.Location | None:
        location = self._geolocator.geocode(address)

        return location  # type: ignore
