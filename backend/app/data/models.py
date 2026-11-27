from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("google_sub", name="uq_users_google_sub"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=text("gen_random_uuid()"))
    google_sub: Mapped[str] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    display_name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    watchlist_items: Mapped[list["WatchlistItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    auth_sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (
        CheckConstraint(
            "ticker <> '' AND ticker = upper(ticker) AND ticker !~ '[[:space:]]'",
            name="ck_watchlist_items_normalized_ticker",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", name="fk_watchlist_items_user_id", ondelete="CASCADE"), primary_key=True
    )
    ticker: Mapped[str] = mapped_column(Text, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="watchlist_items")


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        Index("ix_auth_sessions_user_id", "user_id"),
        Index("ix_auth_sessions_expires_at", "expires_at"),
    )

    token_hash: Mapped[bytes] = mapped_column(LargeBinary, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", name="fk_auth_sessions_user_id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="auth_sessions")


class OAuthLoginAttempt(Base):
    __tablename__ = "oauth_login_attempts"
    __table_args__ = (Index("ix_oauth_login_attempts_expires_at", "expires_at"),)

    state_hash: Mapped[bytes] = mapped_column(LargeBinary, primary_key=True)
    browser_binding_hash: Mapped[bytes] = mapped_column(LargeBinary)
    nonce: Mapped[str] = mapped_column(Text)
    pkce_verifier: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
