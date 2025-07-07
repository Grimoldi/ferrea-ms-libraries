from typing import Protocol

from ferrea.models.datasource import BookDatasource


class ApiService(Protocol):
    """
    This class it's just a protocol about the methods an APIService class should implement.
    """

    @property
    def name(self) -> str:
        """Get the datasource name."""
        ...

    def search_for_book_info(self, isbn: str) -> BookDatasource | None:
        """Search for a book, given the ISBN."""
        ...

    @property
    def healthy(self) -> bool:
        """Health check towards the datasource."""
        ...
