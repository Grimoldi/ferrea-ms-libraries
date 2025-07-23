import json

from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from ferrea.clients.db import DBClient
from ferrea.core.context import Context
from ferrea.core.exceptions import FerreaBaseException
from ferrea.models.error import FerreaError
from ferrea.observability.logs import ferrea_logger
from starlette.responses import JSONResponse

from adapters.libraries import LibrariesRepository
from models.library import Library
from operations.libraries import (
    get_a_library_by_name,
    get_all_libraries,
    upsert_a_library,
)

from ._builder import build_context, build_db_connection

router = APIRouter(prefix="/api/v1")


@cbv(router)
class LibraryViews:
    """
    This class holds the endpoints for the app.
    """

    db_client: DBClient = Depends(build_db_connection)
    context: Context = Depends(build_context)

    @property
    def _repository(self) -> LibrariesRepository:
        return LibrariesRepository(self.db_client)

    @router.get("/libraries")
    def search_all_libraries(self) -> JSONResponse:
        """Endpoint for listing all libraries."""
        ferrea_logger.info(
            "Listing all libraries.",
            **self.context.log,
        )

        try:
            libraries = get_all_libraries(self._repository)
        except FerreaBaseException as e:
            return self._ferrea_exception_5xx(e)
        except Exception as e:
            return self._generic_exception_5xx(e)

        response = {
            "items": len(libraries),
            "result": [
                json.loads(library.model_dump_json(by_alias=True))
                for library in libraries
            ],
        }

        return JSONResponse(
            content=response,
            status_code=status.HTTP_200_OK,
        )

    @router.post("/libraries")
    def create_new_library(self, data: Library) -> JSONResponse:
        """Endpoint for the creation of a new library."""
        ferrea_logger.info(
            f"Creating a new library for {data.name}.",
            **self.context.log,
        )

        try:
            new_library = upsert_a_library(self._repository, data)
        except FerreaBaseException as e:
            return self._ferrea_exception_5xx(e)
        except Exception as e:
            return self._generic_exception_5xx(e)

        return JSONResponse(
            content=json.loads(new_library.model_dump_json(by_alias=True)),
            status_code=status.HTTP_200_OK,
        )

    @router.get("/libraries/{name}")
    def search_library_by_id(self, name: str) -> JSONResponse:
        """Endpoint for search a specific library by name."""
        ferrea_logger.info(
            f"Searching {name} library.",
            **self.context.log,
        )

        try:
            library = get_a_library_by_name(self._repository, name=name)
        except FerreaBaseException as e:
            return self._ferrea_exception_5xx(e)
        except Exception as e:
            return self._generic_exception_5xx(e)

        if not library:
            error = FerreaError(
                uuid=self.context.uuid,
                code="ferrea.libraries.not_found",
                title="Not found",
                message=f"Unable to find library with name {name}.",
            )
            return JSONResponse(
                content=json.loads(error.model_dump_json()),
                status_code=status.HTTP_404_NOT_FOUND,
                headers={"content-type": "application/problem+json"},
            )

        return JSONResponse(
            content=library.model_dump_json(by_alias=True),
            status_code=status.HTTP_200_OK,
        )

    def _ferrea_exception_5xx(self, e: Exception) -> JSONResponse:
        """Helper method for a Ferrea based exception."""
        ferrea_logger.exception(
            f"Received an error specific for Ferrea: {e}.",
            **self.context.log,
        )

        error = FerreaError(
            uuid=self.context.uuid,
            code="ferrea.libraries.error",
            title="Internal server error.",
            message=f"{e}",
        )
        return JSONResponse(
            content=json.loads(error.model_dump_json()),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"content-type": "application/problem+json"},
        )

    def _generic_exception_5xx(self, e: Exception) -> JSONResponse:
        """Helper method for a not Ferrea based exception."""
        ferrea_logger.exception(
            f"Received a generic error: {e}.",
            **self.context.log,
        )

        error = FerreaError(
            uuid=self.context.uuid,
            code="exception.unhandled",
            title="Internal server error.",
            message=f"{e}",
        )
        return JSONResponse(
            content=json.loads(error.model_dump_json()),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"content-type": "application/problem+json"},
        )
