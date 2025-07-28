from ferrea.core.exceptions import FerreaBaseException


class FerreaLibraryNotCreated(FerreaBaseException):
    """Creation of the Library on the db failed."""

    pass


class FerreaNonExistingLibrary(FerreaBaseException):
    """Operation on the library cannot be performed due to non existing library."""

    pass
