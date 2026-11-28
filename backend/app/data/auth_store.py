from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert

from app.data.db import get_session_factory
from app.data.models import AuthSession, OAuthLoginAttempt, User


def save_login_attempt(attempt: OAuthLoginAttempt) -> None:
    with get_session_factory().begin() as session:
        session.execute(delete(OAuthLoginAttempt).where(OAuthLoginAttempt.expires_at <= func.now()))
        session.add(attempt)


def consume_login_attempt(state_hash: bytes, binding_hash: bytes) -> tuple[str, str] | None:
    with get_session_factory().begin() as session:
        attempt = session.execute(
            delete(OAuthLoginAttempt)
            .where(
                OAuthLoginAttempt.state_hash == state_hash,
                OAuthLoginAttempt.browser_binding_hash == binding_hash,
                OAuthLoginAttempt.expires_at > func.now(),
            )
            .returning(OAuthLoginAttempt.nonce, OAuthLoginAttempt.pkce_verifier)
        ).one_or_none()
        return tuple(attempt) if attempt is not None else None


def create_session(
    google_sub: str, email: str | None, display_name: str | None,
    token_hash: bytes, expires_at: datetime, previous_token_hash: bytes | None,
) -> None:
    with get_session_factory().begin() as session:
        profile = insert(User).values(google_sub=google_sub, email=email, display_name=display_name)
        user_id: UUID = session.execute(
            profile.on_conflict_do_update(
                index_elements=[User.google_sub],
                set_={"email": profile.excluded.email, "display_name": profile.excluded.display_name,
                      "updated_at": func.now()},
            ).returning(User.id)
        ).scalar_one()
        session.execute(delete(AuthSession).where(AuthSession.expires_at <= func.now()))
        if previous_token_hash is not None:
            session.execute(update(AuthSession).where(
                AuthSession.token_hash == previous_token_hash, AuthSession.revoked_at.is_(None)
            ).values(revoked_at=func.now()))
        session.add(AuthSession(token_hash=token_hash, user_id=user_id, expires_at=expires_at))


def find_session_user(token_hash: bytes) -> User | None:
    with get_session_factory()() as session:
        return session.scalar(select(User).join(AuthSession).where(
            AuthSession.token_hash == token_hash,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > func.now(),
        ))


def revoke_session(token_hash: bytes) -> None:
    with get_session_factory().begin() as session:
        session.execute(update(AuthSession).where(
            AuthSession.token_hash == token_hash, AuthSession.revoked_at.is_(None)
        ).values(revoked_at=func.now()))
