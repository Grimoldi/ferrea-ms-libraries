from ferrea.core.context import Context
from ferrea.models.datasource import BookDatasource
from ferrea.observability.logs import ferrea_logger

from models.api_service import ApiService


def fetch_data(
    isbn: str,
    datasources: list[ApiService],
    context: Context,
) -> BookDatasource | None:
    """From all the registered datasources, try to fetch the data.

    Args:
        isbn (str): the book isbn.
        datasources (list[ApiService]): the list of all configured datasources.
        context (Context): the api request context.

    Returns:
        BookDatasource | None: the instance with the fetched information or None if not found.
    """
    ferrea_logger.info(
        "Start searching external datasources for book data.",
        **context.log,
    )
    for datasource in datasources:
        book_data = datasource.search_for_book_info(
            isbn
        )  # TODO: right now returns just the latest. Implement a logic for the multiple datasources.

    return book_data
