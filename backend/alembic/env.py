from alembic import context
from alembic.util import CommandError
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from app.config import DatabaseConfigError, load_database_settings
from app.data.db import create_database_engine
from app.data.models import Base


def run_migrations_offline() -> None:
    context.configure(dialect_name="postgresql", literal_binds=True, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=Base.metadata, compare_server_default=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = context.config.attributes.get("connection")
    if connection is not None:
        run_migrations(connection)
        return

    try:
        engine = create_database_engine(load_database_settings())
        try:
            with engine.connect() as connection:
                run_migrations(connection)
        finally:
            engine.dispose()
    except DatabaseConfigError as exc:
        raise CommandError(f"Database configuration error: {exc}") from None
    except (SQLAlchemyError, ValueError):
        raise CommandError("PostgreSQL migration failed. Verify the database settings, schema, and permissions.") from None


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
