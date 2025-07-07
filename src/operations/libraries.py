from models.library import Library
from models.repository import RepositoryService


def get_all_libraries(repository: RepositoryService) -> list[Library]:
    """_summary_

    Args:
        repository (RepositoryService): _description_

    Returns:
        list[Library]: _description_
    """

    return repository.find_all_libraries()


def get_a_library_by_name(repository: RepositoryService, name: str) -> Library | None:
    """_summary_

    Args:
        repository (RepositoryService): _description_

    Returns:
        Library | None: _description_
    """
    return repository.find_a_library(name)


def upsert_a_library(repository: RepositoryService, library: Library) -> Library:
    """_summary_

    Args:
        repository (RepositoryService): _description_
        library (Library): _description_

    Returns:
        Library: _description_
    """
    return repository.create_library(library)
