from ferrea.observability.logs import ferrea_logger

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


def get_library_by_fid(repository: RepositoryService, fid: str) -> Library | None:
    """Search for a specific library in the repository.

    Args:
        repository (RepositoryService): the repository instance.
        name (str): the name of the library.

        Returns:
            Library | None: the library found or None if not found.
    """
    try:
        return repository.find_a_library_by_fid(fid)
    except FerreaNonExistingLibrary as _:
        return None


def upsert_library(repository: RepositoryService, library: Library) -> Library:
    """Created a new library or update an already existing one.

    Args:
        repository (RepositoryService): the repository instance.
        library (Library): the library data.

    Returns:
        Library: the created Library.
    """
    return repository.create_library(library)


def update_library(
    repository: RepositoryService,
    fid: str,
    new_library: Library,
) -> Library | None:
    """Update an already existing library.

    Args:
        repository (RepositoryService): the repository instance.
        fid (str): the object fid (ferrea id)
        library (Library): the library data.

    Returns:
        Library | None: the updatedlibrary or None if not found.
    """
    ferrea_logger.info(f"Start updating library with fid {fid}.")
    try:
        return repository.update_library(fid, new_library)
    except FerreaNonExistingLibrary as _:
        return None


def delete_library(
    repository: RepositoryService,
    fid: str,
) -> Library | None:
    """Deletes an already existing library.

    Args:
        repository (RepositoryService): the repository instance.
        fid (str): the object fid (ferrea id)
        library (Library): the library data.

    Returns:
        Library | None: the deleted or None if not found.
    """
    try:
        return repository.delete_library(fid)
    except FerreaNonExistingLibrary as _:
        return None
