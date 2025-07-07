from pathlib import Path

import uvicorn
from configs import settings
from fastapi import FastAPI
from ferrea.core.oas import add_openapi_schema
from ferrea.observability.logs import setup_logger

from routers import datasources, probes


def app() -> FastAPI:
    """Setup the app with custom logic, as well as adding the routers."""
    app = FastAPI()
    if settings.ferrea_app.oas_path is not None:
        app = add_openapi_schema(app, Path(settings.ferrea_app.oas_path))

    app.include_router(datasources.router)
    app.include_router(probes.router)

    return app


if __name__ == "__main__":
    setup_logger()
    uvicorn.run(
        "app:app",
        port=8080,
        factory=True,
        access_log=False,
        log_level=None,
        log_config=None,
    )
