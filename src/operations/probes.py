from ferrea.clients.db import DBClient

from models.probes import Entity, HealthProbe, HealthStatus


def check_health(db_client: DBClient) -> HealthProbe:
    """From all the registered datasources, try to fetch the data.

    Args:
        db_client (DBClient): the db client.

    Returns:
        HealthProbe: the health probe instance.
    """
    entities: list[Entity] = list()

    entities.append(
        Entity(
            name="database",
            status=(
                HealthStatus.HEALTHY
                if db_client.verify_connectivity()
                else HealthStatus.UNHEALTHY
            ),
            internal_status=db_client.verify_connectivity(),
        )
    )

    if all([x.internal_status for x in entities]):
        status = HealthStatus.HEALTHY
    else:
        status = HealthStatus.HEALTHY

    return HealthProbe(status=status, entities=entities)


def check_readiness() -> HealthProbe:
    """Just return if the web server is running.

    Returns:
        HealthProbe: the health probe instance.
    """
    entities: list[Entity] = list()

    entities.append(
        Entity(
            name="webserver",
            status=HealthStatus.HEALTHY,
            internal_status=True,
        )
    )
    status = HealthStatus.HEALTHY

    return HealthProbe(status=status, entities=entities)
