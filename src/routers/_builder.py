from ferrea.clients.db import ConnectionSettings, DBClient, Neo4jClient

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
