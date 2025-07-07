from models.api_service import ApiService
from models.probes import Entity, HealthProbe, HealthStatus


def check_health(datasources: list[ApiService]) -> HealthProbe:
    """From all the registered datasources, try to fetch the data.

    Args:
        datasources (list[ApiService]): the list of all datasources configured.

    Returns:
        HealthProbe: the health probe instance.
    """
    entities: list[Entity] = list()

    for datasource in datasources:
        entities.append(
            Entity(
                name=datasource.name,
                status=(
                    HealthStatus.HEALTHY
                    if datasource.healthy
                    else HealthStatus.UNHEALTHY
                ),
                internal_status=datasource.healthy,
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
