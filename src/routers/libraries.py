from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from ferrea.clients.db import ConnectionSettings, DBClient, Neo4jClient
from starlette.responses import JSONResponse

from adapters.libraries import LibrariesRepository
from configs.config import settings
from models.library import Library
from operations.libraries import (
    get_a_library_by_name,
    get_all_libraries,
    upsert_a_library,
)

router = APIRouter()


def get_db() -> DBClient:
    """
    This function just returns the instance of the db object.
    Needed a funcion for the "Depends" on fastapi.

    Returns:
        type[DBClient]: an instance that matches the DBClient protocol.
    """
    db_conf = settings.database
    if db_conf.database is None:
        connection_settings = ConnectionSettings(
            db_conf.uri,
            db_conf.username,
            db_conf.password,
        )
    else:
        connection_settings = ConnectionSettings(
            db_conf.uri,
            db_conf.username,
            db_conf.password,
            db_conf.database,
        )

    return Neo4jClient(connection_settings=connection_settings)


@cbv(router)
class LibraryViews:
    """
    This class holds the endpoints for the app.
    """

    db_client: DBClient = Depends(get_db)

    def __post_init__(self) -> None:
        self._repository = LibrariesRepository(self.db_client)

    @router.get("/libraries")
    def search_all_libraries(self) -> JSONResponse:
        libraries = get_all_libraries(self._repository)
        if libraries:
            return JSONResponse(
                content=[
                    library.model_dump_json(by_alias=True) for library in libraries
                ],
                status_code=status.HTTP_200_OK,
            )
        else:
            return JSONResponse(
                content="not found", status_code=status.HTTP_404_NOT_FOUND
            )

    @router.get("/libraries/{name}")
    def search_library_by_id(self, name: str) -> JSONResponse:
        library = get_a_library_by_name(self._repository, name=name)

        if library:
            return JSONResponse(
                content=library.model_dump_json(by_alias=True),
                status_code=status.HTTP_200_OK,
            )
        else:
            return JSONResponse(
                content="not found", status_code=status.HTTP_404_NOT_FOUND
            )

    @router.post("/libraries")
    def create_new_library(self, data: Library) -> JSONResponse:
        new_library = upsert_a_library(self._repository, data)
        return JSONResponse(
            content=new_library.model_dump_json(by_alias=True),
            status_code=status.HTTP_200_OK,
        )
