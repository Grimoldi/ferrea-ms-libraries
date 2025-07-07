from dataclasses import dataclass
from typing import ContextManager, Protocol

from ferrea.clients.db import DBClient

from models.library import Library


@dataclass
class RepositoryService(Protocol):
    """
    This class it's just a protocol about the methods an Repository class should implement.
    """

    db_client: ContextManager[DBClient]

    def find_all_libraries(self) -> list[Library]:
        """
        This method gets all libraries on the db.

        Returns:
            list[Library]: the list of all Libraries.
        """
        ...

    def find_a_library(self, name: str) -> Library | None:
        """
        This method search for the desired library on the db.

        Args:
            name (str): the name of the library.

        Returns:
            Library | None: the library if found, else None.
        """
        ...

    def create_library(self, data: Library) -> Library:
        """
        This method creates a library on the db.

        Args:
            data (Library): the data of the library to create.

        Returns:
            Library: the created library.
        """
        ...
