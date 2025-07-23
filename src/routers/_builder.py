from fastapi import Request
from ferrea.clients.db import ConnectionSettings, DBClient, Neo4jClient
from ferrea.core.context import Context
from ferrea.core.header import FERRA_CORRELATION_HEADER, get_correlation_id

from configs.config import settings


def build_db_connection() -> DBClient:
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


async def build_context(request: Request) -> Context:
    """Build a context from the request.

    Args:
        request (Request): the HTTP Request.

    Returns:
        Context: the context of the call.
    """
    ferrea_correlation_id = request.headers.get(FERRA_CORRELATION_HEADER)
    correlation_id = await get_correlation_id(ferrea_correlation_id)
    return Context(str(correlation_id), settings.ferrea_app.name)
