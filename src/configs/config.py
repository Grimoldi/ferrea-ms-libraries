from pathlib import Path

from dynaconf.typed import Annotated, DictValue, Dynaconf, Options
from dynaconf.typed.validators import Validator

config_dir = Path(__file__).parent


class Openlibrary(DictValue):
    """Settings for the Openlibrary datasource."""

    api_url: Annotated[str, Validator(startswith="https://")]
    cover_url: Annotated[str, Validator(startswith="https://")]
    name: str


class Google(DictValue):
    """Settings for the Google Books datasource."""

    api_url: Annotated[str, Validator(startswith="https://")]
    name: str


class FerreaApp(DictValue):
    """Settings for the app itself."""

    name: str
    debug: bool = False
    oas_path: str | None = None


class FerreaSettings(Dynaconf):
    """Overall settings for the webserver."""

    ferrea_app: FerreaApp = FerreaApp()  # type: ignore
    google: Google = Google()  # type: ignore
    openlibrary: Openlibrary = Openlibrary()  # type: ignore

    dynaconf_options = Options(
        envvar_prefix="FERREA",
        settings_files=["settings.toml", ".secrets.toml"],
        root_path=config_dir,
    )


settings = FerreaSettings(_debug_mode=False)
