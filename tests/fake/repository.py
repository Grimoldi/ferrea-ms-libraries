import random
import uuid
from dataclasses import dataclass
from typing import ContextManager

from ferrea.clients.db import DBClient
from ferrea.core.context import Context

from models.exceptions import FerreaNonExistingLibrary
from models.library import Library


@dataclass
class FakeRepository:

    db_client: ContextManager[DBClient]
    context: Context

    def __post_init__(self) -> None:
        self._graph: list[Library] = []

    def find_all_libraries(self) -> list[Library]:
        return self._graph

    def find_a_library_by_fid(self, fid: str) -> Library:
        [library_found] = [x for x in self._graph if x.fid == fid]

        if library_found is None:
            raise FerreaNonExistingLibrary(
                f"Unable to find library based on the provided fid {fid}."
            )
        return library_found

    def create_library(self, data: Library) -> Library:
        self._graph.append(self._hydrate_data(data))

        return data

    def update_library(self, fid: str, new_value: Library) -> Library:
        if fid not in [x.fid for x in self._graph]:
            raise FerreaNonExistingLibrary(
                f"Unable to find library based on the provided fid {fid}."
            )

        for index, lib in enumerate(self._graph):
            if lib.fid == fid:
                self._graph.pop(index)
                self._graph.insert(index, self._hydrate_data(new_value))
        return new_value

    def delete_library(self, fid: str) -> Library:
        for index, lib in enumerate(self._graph):
            if lib.fid == fid:
                old_library = self._graph.pop(index)
        return old_library

    def _hydrate_data(self, input_data: Library) -> Library:
        """Add read only properties."""
        if input_data.fid is None:
            input_data.fid = str(uuid.uuid4())
        input_data.latitude = random.random()
        input_data.longitude = random.random()

        return input_data
