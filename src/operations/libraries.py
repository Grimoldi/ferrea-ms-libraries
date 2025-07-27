from models.exceptions import FerreaNonExistingLibrary
from models.library import Library
from models.repository import RepositoryService


def get_all_libraries(repository: RepositoryService) -> list[Library]:
    """Get all libraries stored in the repository.

    Args:
        repository (RepositoryService): the repository instance.

    Returns:
        list[Library]: the list of all libraries in the repository.
    """

    return repository.find_all_libraries()


def get_a_library_by_fid(repository: RepositoryService, fid: str) -> Library | None:
    """Search for a specific library in the repository.

    Args:
        repository (RepositoryService): the repository instance.
        name (str): the name of the library.

        Returns:
            Library: the library found or None.
    """
    try:
        return repository.find_a_library_by_fid(fid)
    except FerreaNonExistingLibrary as _:
        return None


def upsert_a_library(repository: RepositoryService, library: Library) -> Library:
    """Created a new library or update an already existing one.

    Args:
        repository (RepositoryService): the repository instance.
        library (Library): the library data.

    Returns:
        Library: the created Library.
    """
    return repository.create_library(library)
