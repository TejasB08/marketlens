import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit


_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
_DATABASE_KEYS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
_AUTH_KEYS = ("AUTH_PUBLIC_ORIGIN", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET")


class DatabaseConfigError(ValueError):
    """Invalid or missing database configuration."""


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str = field(repr=False)


class AuthConfigError(ValueError):
    """Invalid or missing authentication configuration."""


@dataclass(frozen=True)
class AuthSettings:
    origin: str
    google_client_id: str
    google_client_secret: str = field(repr=False)

    @property
    def secure_cookies(self) -> bool:
        return self.origin.startswith("https://")


def _read_local_settings(keys: set[str]) -> dict[str, str]:
    try:
        contents = _ENV_FILE.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeError):
        raise ValueError("Could not read backend/.env as UTF-8.") from None

    values = {}
    for line in contents.splitlines():
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or key not in keys:
            continue

        value = value.strip()
        if value.startswith(("'", '"')):
            if len(value) < 2 or not value.endswith(value[0]):
                raise ValueError(f"Unclosed quoted value for {key} in backend/.env.")
            value = value[1:-1]
        values[key] = value
    return values


def _read_settings(keys: tuple[str, ...]) -> dict[str, str]:
    values = {key: os.environ[key] for key in keys if key in os.environ}
    missing = set(keys).difference(values)
    if missing:
        values.update(_read_local_settings(missing))
    return values


def load_database_settings() -> DatabaseSettings:
    try:
        values = _read_settings(_DATABASE_KEYS)
    except ValueError as exc:
        raise DatabaseConfigError(str(exc)) from None
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


def load_auth_settings() -> AuthSettings:
    try:
        values = _read_settings(_AUTH_KEYS)
    except ValueError as exc:
        raise AuthConfigError(str(exc)) from None
    if any(not values.get(key) for key in _AUTH_KEYS):
        raise AuthConfigError("Set AUTH_PUBLIC_ORIGIN, GOOGLE_CLIENT_ID, and GOOGLE_CLIENT_SECRET.")

    origin = values["AUTH_PUBLIC_ORIGIN"]
    try:
        parsed = urlsplit(origin)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        raise AuthConfigError("Invalid AUTH_PUBLIC_ORIGIN.") from None
    if (
        not host or parsed.username is not None or parsed.path not in ("", "/")
        or parsed.query or parsed.fragment or any(char.isspace() for char in origin)
        or (parsed.scheme != "https" and not (
            parsed.scheme == "http" and host in ("localhost", "127.0.0.1", "::1")
        ))
    ):
        raise AuthConfigError("AUTH_PUBLIC_ORIGIN must be an HTTPS origin or a loopback HTTP origin.")

    authority = f"[{host}]" if ":" in host else host
    if port is not None and port != (443 if parsed.scheme == "https" else 80):
        authority += f":{port}"
    return AuthSettings(f"{parsed.scheme}://{authority}", values["GOOGLE_CLIENT_ID"], values["GOOGLE_CLIENT_SECRET"])
