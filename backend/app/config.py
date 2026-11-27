import os
from dataclasses import dataclass, field
from pathlib import Path


_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
_DATABASE_KEYS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")


class DatabaseConfigError(ValueError):
    """Invalid or missing database configuration."""


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str = field(repr=False)


def _read_local_database_settings(keys: set[str]) -> dict[str, str]:
    try:
        contents = _ENV_FILE.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeError):
        raise DatabaseConfigError("Could not read backend/.env as UTF-8.") from None

    values = {}
    for line in contents.splitlines():
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or key not in keys:
            continue

        value = value.strip()
        if value.startswith(("'", '"')):
            if len(value) < 2 or not value.endswith(value[0]):
                raise DatabaseConfigError(f"Unclosed quoted value for {key} in backend/.env.")
            value = value[1:-1]
        values[key] = value
    return values


def load_database_settings() -> DatabaseSettings:
    values = {key: os.environ[key] for key in _DATABASE_KEYS if key in os.environ}
    missing = set(_DATABASE_KEYS).difference(values)
    if missing:
        values.update(_read_local_database_settings(missing))

    empty = [key for key in _DATABASE_KEYS if not values.get(key)]
    if empty:
        raise DatabaseConfigError(f"Missing database settings: {', '.join(empty)}.")

    try:
        port = int(values["DB_PORT"])
    except ValueError:
        raise DatabaseConfigError("DB_PORT must be an integer from 1 to 65535.") from None
    if not 1 <= port <= 65535:
        raise DatabaseConfigError("DB_PORT must be an integer from 1 to 65535.")

    return DatabaseSettings(
        host=values["DB_HOST"],
        port=port,
        database=values["DB_NAME"],
        user=values["DB_USER"],
        password=values["DB_PASSWORD"],
    )
