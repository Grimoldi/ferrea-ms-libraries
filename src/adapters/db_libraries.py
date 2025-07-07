from typing import ContextManager

import geopy
from attr import define
from ferrea.clients.db import DBClient

from models.library import Library


@define
class LibrariesOperation:
    db: ContextManager[DBClient]

    def find_all_libraries(self) -> list[Library]:
        """
        This method gets all libraries on the db.

        Returns:
            list[Library]: the list of all Libraries.
        """
        query = "MATCH (l:Library) return l"
        with self.db as session:
            libraries_raw = session.read(query=query)
        libraries = list()

        for library in libraries_raw:
            temp = dict(library[0].items())
            libraries.append(Library(**temp))

        return libraries

    def find_library(self, name: str) -> Library | None:
        """
        This method search for the desired library on the db.

        Args:
            name (str): the name of the library.

        Returns:
            Library | None: the library if found, else None.
        """
        query = "MATCH (l:Library) WHERE l.name = $library_name RETURN l"
        params = {"library_name": name}

        with self.db as session:
            library_raw = session.read(query, params)  # type: ignore

        if len(library_raw) == 0:
            return

        temp = dict(library_raw[0][0].items())
        return Library(**temp)

    def create_library(self, data: Library) -> Library:
        """
        This method creates a library on the db.

        Args:
            data (CreateLibrary): the data of the library to create.

        Returns:
            Library: the created library.
        """
        geolocator = geopy.Nominatim(user_agent="my_geo_coder")
        location = self._find_location(data.address, geolocator)

        query = (
            "MERGE (l:Library {name: $name, phone: $phone, address: $address, email: $email, location: "
            "point({latitude: $latitude, longitude: $longitude})})"
        )
        params = {
            "name": data.name,
            "phone": data.phone,
            "address": data.address,
            "email": data.email,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
        with self.db as session:
            session.write(query, params)

        return Library(data.name, data.address, location, data.email, data.phone)  # type: ignore

    def _find_location(
        self, address: str, geolocator: geopy.Nominatim
    ) -> geopy.Location:
        location = geolocator.geocode(address)

        return location  # type: ignore
