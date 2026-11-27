import sys
from functools import cache
from threading import Lock

from sqlalchemy import URL, Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config import DatabaseConfigError, DatabaseSettings, load_database_settings


_initialization_lock = Lock()


def create_database_engine(settings: DatabaseSettings) -> Engine:
    """Build a PostgreSQL engine from explicit settings without opening a connection."""
    url = URL.create(
        "postgresql+psycopg",
        username=settings.user,
        password=settings.password,
        host=settings.host,
        port=settings.port,
        database=settings.database,
    )
    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
        echo=False,
        hide_parameters=True,
    )


@cache
def _create_database() -> tuple[Engine, sessionmaker[Session]]:
    engine = create_database_engine(load_database_settings())
    return engine, sessionmaker(bind=engine)


def _get_database() -> tuple[Engine, sessionmaker[Session]]:
    with _initialization_lock:
        return _create_database()


def get_session_factory() -> sessionmaker[Session]:
    """Return the shared factory. Open a separate session per operation."""
    _, factory = _get_database()
    return factory


def main() -> int:
    try:
        engine, factory = _get_database()
        try:
            with factory() as session:
                session.execute(text("SELECT 1")).scalar_one()
        finally:
            engine.dispose()
    except DatabaseConfigError as exc:
        print(f"Database configuration error: {exc}", file=sys.stderr)
        return 1
    except (SQLAlchemyError, ValueError):
        print("PostgreSQL connection check failed. Verify the server and database settings.", file=sys.stderr)
        return 1

    print("PostgreSQL connection verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
