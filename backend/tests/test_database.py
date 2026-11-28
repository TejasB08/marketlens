import os
import unittest
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import delete, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import DatabaseSettings
from app.data.db import create_database_engine
from app.data.models import AuthSession, Base, OAuthLoginAttempt, User, WatchlistItem


def _load_test_settings() -> DatabaseSettings:
    values = {key: os.environ.get(f"MARKETLENS_TEST_DB_{key}", "") for key in ("HOST", "PORT", "NAME", "USER", "PASSWORD")}
    if not all(values.values()) or not values["NAME"].startswith("marketlens_test_"):
        raise RuntimeError("Set all MARKETLENS_TEST_DB_* variables for an empty marketlens_test_* database.")
    return DatabaseSettings(values["HOST"], int(values["PORT"]), values["NAME"], values["USER"], values["PASSWORD"])


def digest(value: str) -> bytes:
    return sha256(value.encode()).digest()


class PostgreSQLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings = _load_test_settings()
        engine = create_database_engine(settings)
        cls.addClassCleanup(engine.dispose)
        cls.connection = cls.enterClassContext(engine.connect())
        transaction = cls.connection.begin()
        cls.addClassCleanup(transaction.rollback)

        if cls.connection.scalar(text("SELECT current_database()")) != settings.database:
            raise RuntimeError("The connected database does not match the disposable test database name.")
        cls.connection.execute(text("SET LOCAL search_path TO public"))
        inspector = inspect(cls.connection)
        if inspector.get_table_names(schema="public") or inspector.get_view_names(schema="public"):
            raise RuntimeError("The disposable test database must start with an empty public schema.")

        cls.migrations = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        cls.migrations.attributes["connection"] = cls.connection
        command.upgrade(cls.migrations, "head")

    def setUp(self):
        savepoint = self.connection.begin_nested()
        self.addCleanup(savepoint.rollback)


class DatabaseTests(PostgreSQLTestCase):
    def setUp(self):
        super().setUp()
        self.session = self.enterContext(Session(bind=self.connection, join_transaction_mode="create_savepoint"))
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    def user(self, subject: str, **profile) -> User:
        user = User(google_sub=subject, **profile)
        self.session.add(user)
        self.session.flush()
        return user

    def assert_integrity_error(self, sqlstate: str, row) -> None:
        with self.assertRaises(IntegrityError) as error:
            with self.session.begin_nested():
                self.session.add(row)
                self.session.flush()
        self.assertEqual(error.exception.orig.sqlstate, sqlstate)

    def test_migration_round_trip_and_metadata(self):
        expected_tables = set(Base.metadata.tables) | {"alembic_version"}
        self.assertEqual(set(inspect(self.connection).get_table_names()), expected_tables)
        command.check(self.migrations)
        command.downgrade(self.migrations, "base")
        self.assertEqual(inspect(self.connection).get_table_names(), ["alembic_version"])
        command.upgrade(self.migrations, "head")
        self.assertEqual(set(inspect(self.connection).get_table_names()), expected_tables)
        command.check(self.migrations)

    def test_subject_unique_and_email_is_profile_data(self):
        first = self.user("subject-one", email="shared@example.test")
        second = self.user("subject-two", email="shared@example.test")
        self.assertNotEqual(first.id, second.id)
        self.assert_integrity_error("23505", User(google_sub="subject-one"))
        self.assert_integrity_error("23502", User())

    def test_duplicate_watchlist_item_is_rejected(self):
        user = self.user("watchlist-user")
        self.session.add(WatchlistItem(user_id=user.id, ticker="RELIANCE.NS"))
        self.session.flush()
        self.assert_integrity_error("23505", WatchlistItem(user_id=user.id, ticker="RELIANCE.NS"))

    def test_watchlist_isolation_with_owner_scoped_queries(self):
        first, second = self.user("first"), self.user("second")
        self.session.add_all([
            WatchlistItem(user_id=first.id, ticker="TCS.NS"),
            WatchlistItem(user_id=second.id, ticker="TCS.NS"),
            WatchlistItem(user_id=second.id, ticker="INFY.NS"),
        ])
        self.session.flush()

        def tickers(user_id):
            statement = select(WatchlistItem.ticker).where(WatchlistItem.user_id == user_id)
            return set(self.session.scalars(statement))

        self.assertEqual(tickers(first.id), {"TCS.NS"})
        self.assertEqual(tickers(second.id), {"TCS.NS", "INFY.NS"})
        self.session.execute(delete(WatchlistItem).where(
            WatchlistItem.user_id == first.id, WatchlistItem.ticker == "TCS.NS"
        ))
        self.assertEqual(tickers(first.id), set())
        self.assertEqual(tickers(second.id), {"TCS.NS", "INFY.NS"})

    def test_ticker_must_be_normalized(self):
        user = self.user("normalization-user")
        for ticker in ("", "tcs.ns", " TCS.NS ", "TCS\t.NS"):
            with self.subTest(ticker=ticker):
                self.assert_integrity_error("23514", WatchlistItem(user_id=user.id, ticker=ticker))

    def test_foreign_keys_require_a_user(self):
        missing_user = uuid4()
        self.assert_integrity_error("23503", WatchlistItem(user_id=missing_user, ticker="INFY.NS"))
        self.assert_integrity_error("23503", AuthSession(
            token_hash=digest("orphan"), user_id=missing_user, expires_at=self.expires_at
        ))

    def test_relationships_and_timestamps(self):
        user = self.user("relational-user")
        watch = WatchlistItem(ticker="TCS.NS")
        auth = AuthSession(token_hash=digest("token"), expires_at=self.expires_at)
        state = OAuthLoginAttempt(
            state_hash=digest("state"), browser_binding_hash=digest("browser"),
            nonce="nonce", pkce_verifier="verifier", expires_at=self.expires_at,
        )
        user.watchlist_items.append(watch)
        user.auth_sessions.append(auth)
        self.session.add(state)
        self.session.flush()
        self.session.expire_all()

        self.assertEqual(user.watchlist_items, [watch])
        self.assertEqual(user.auth_sessions, [auth])
        self.assertIs(watch.user, user)
        self.assertIs(auth.user, user)
        self.assertIsNone(auth.revoked_at)
        auth.revoked_at = self.expires_at
        self.session.flush()
        self.session.refresh(auth)
        for timestamp in (
            user.created_at, user.updated_at, watch.created_at, auth.created_at,
            auth.expires_at, auth.revoked_at, state.expires_at,
        ):
            self.assertIsNotNone(timestamp.utcoffset())

    def test_user_delete_cascades_in_postgresql(self):
        user = self.user("delete-owner")
        other = self.user("keep-owner")
        user_id = user.id
        self.session.add_all([
            WatchlistItem(user_id=user_id, ticker="TCS.NS"),
            WatchlistItem(user_id=other.id, ticker="TCS.NS"),
            AuthSession(user_id=user_id, token_hash=digest("deleted"), expires_at=self.expires_at),
            AuthSession(user_id=other.id, token_hash=digest("kept"), expires_at=self.expires_at),
        ])
        self.session.flush()
        self.connection.execute(delete(User.__table__).where(User.id == user_id))
        self.assertEqual(list(self.session.scalars(select(WatchlistItem.user_id))), [other.id])
        self.assertEqual(list(self.session.scalars(select(AuthSession.user_id))), [other.id])

    def test_auth_hashes_are_unique(self):
        user = self.user("session-owner")
        token_hash = digest("duplicate-token")
        state_hash = digest("duplicate-state")
        self.session.add(AuthSession(user_id=user.id, token_hash=token_hash, expires_at=self.expires_at))
        attempt = dict(
            state_hash=state_hash, browser_binding_hash=digest("browser"),
            nonce="nonce", pkce_verifier="verifier", expires_at=self.expires_at,
        )
        self.session.add(OAuthLoginAttempt(**attempt))
        self.session.flush()
        self.assert_integrity_error("23505", AuthSession(
            user_id=user.id, token_hash=token_hash, expires_at=self.expires_at
        ))
        self.assert_integrity_error("23505", OAuthLoginAttempt(**attempt))
