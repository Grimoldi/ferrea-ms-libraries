import json

from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from ferrea.core.context import Context
from ferrea.core.exceptions import FerreaBaseException
from ferrea.core.header import FERRA_CORRELATION_HEADER
from ferrea.models.error import FerreaError
from ferrea.observability.logs import ferrea_logger
from starlette.responses import JSONResponse

from models.library import Library
from models.repository import RepositoryService
from operations.libraries import (
    delete_library,
    get_all_libraries,
    get_library_by_fid,
    update_library,
    upsert_library,
)

from ._builder import build_context, build_repository

router = APIRouter(prefix="/api/v1")


@cbv(router)
class LibraryViews:
    """
    This class holds the endpoints for the app.
    """

    context: Context = Depends(build_context)
    _repository: RepositoryService = Depends(build_repository)

    @property
    def _headers(self) -> dict[str, str]:
        return {FERRA_CORRELATION_HEADER: self.context.uuid}

    @router.get("/libraries", response_model=None)
    def get_all_libraries_entrypoint(self) -> JSONResponse:
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
            headers=self._headers,
        )

    @router.post("/libraries", response_model=None)
    def create_library_entrypoint(self, data: Library) -> JSONResponse:
        """Endpoint for the creation of a new library."""
        ferrea_logger.info(
            f"Creating a new library for {data.name}.",
            **self.context.log,
        )

        try:
            new_library = upsert_library(self._repository, data)
        except FerreaBaseException as e:
            return self._ferrea_exception_5xx(e)
        except Exception as e:
            return self._generic_exception_5xx(e)

        return JSONResponse(
            content=json.loads(new_library.model_dump_json(by_alias=True)),
            status_code=status.HTTP_200_OK,
            headers=self._headers,
        )

    @router.get("/libraries/{fid}", response_model=None)
    def search_library_entrypoint(self, fid: str) -> JSONResponse:
        """Endpoint for search a specific library by its fid (ferrea id)."""
        ferrea_logger.info(
            f"Searching {fid} library.",
            **self.context.log,
        )

        try:
            library = get_library_by_fid(self._repository, fid=fid)
        except FerreaBaseException as e:
            return self._ferrea_exception_5xx(e)
        except Exception as e:
            return self._generic_exception_5xx(e)

        if not library:
            return self._not_found(fid)

        return JSONResponse(
            content=json.loads(library.model_dump_json(by_alias=True)),
            status_code=status.HTTP_200_OK,
            headers=self._headers,
        )

    @router.put("/libraries/{fid}", response_model=None)
    def update_library_entrypoint(self, fid: str, data: Library) -> JSONResponse:
        """Endpoint for update a specific library by its fid (ferrea id)."""
        ferrea_logger.info(
            f"Updating {fid} library.",
            **self.context.log,
        )

        try:
            library = update_library(self._repository, fid=fid, new_library=data)
        except FerreaBaseException as e:
            return self._ferrea_exception_5xx(e)
        except Exception as e:
            return self._generic_exception_5xx(e)

        if not library:
            return self._not_found(fid)

        return JSONResponse(
            content=json.loads(library.model_dump_json(by_alias=True)),
            status_code=status.HTTP_200_OK,
            headers=self._headers,
        )

    @router.delete("/libraries/{fid}", response_model=None)
    def delete_library_entrypoint(self, fid: str) -> JSONResponse:
        """Endpoint to delete a specific library by its fid (ferrea id)."""
        ferrea_logger.info(
            f"Deleting {fid} library.",
            **self.context.log,
        )

        try:
            library = delete_library(self._repository, fid=fid)
        except FerreaBaseException as e:
            return self._ferrea_exception_5xx(e)
        except Exception as e:
            return self._generic_exception_5xx(e)

        if not library:
            return self._not_found(fid)

        return JSONResponse(
            content={},
            status_code=status.HTTP_204_NO_CONTENT,
            headers=self._headers,
        )

    def _not_found(self, fid: str) -> JSONResponse:
        """Helper method for not found libraries."""
        error = FerreaError(
            uuid=self.context.uuid,
            code="ferrea.libraries.not_found",
            title="Not found",
            message=f"Unable to find library with fid {fid}.",
        )
        self._headers.update({"content-type": "application/problem+json"})

        return JSONResponse(
            content=json.loads(error.model_dump_json()),
            status_code=status.HTTP_404_NOT_FOUND,
            headers=self._headers,
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
        self._headers.update({"content-type": "application/problem+json"})

        return JSONResponse(
            content=json.loads(error.model_dump_json()),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=self._headers,
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
        self._headers.update({"content-type": "application/problem+json"})

        return JSONResponse(
            content=json.loads(error.model_dump_json()),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=self._headers,
        )
