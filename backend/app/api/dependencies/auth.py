import hmac
from dataclasses import dataclass, field
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError

from app.config import AuthConfigError, AuthSettings, DatabaseConfigError, load_auth_settings
from app.data.auth_store import find_session_user
from app.schemas.auth_schema import CurrentUser
from app.services.auth_service import csrf_token, opaque_hash


@dataclass(frozen=True)
class AuthenticatedSession:
    user: CurrentUser
    token_hash: bytes = field(repr=False)
    csrf: str = field(repr=False)


def auth_unavailable() -> HTTPException:
    return HTTPException(status_code=503, detail="Authentication temporarily unavailable.")


def get_auth_settings() -> AuthSettings:
    try:
        return load_auth_settings()
    except AuthConfigError:
        raise auth_unavailable() from None


AuthConfig = Annotated[AuthSettings, Depends(get_auth_settings)]


def cookie_name(settings: AuthSettings, kind: str) -> str:
    prefix = "__Host-" if settings.secure_cookies else ""
    return f"{prefix}marketlens_{kind}"


def get_optional_session(request: Request, settings: AuthConfig) -> AuthenticatedSession | None:
    token = request.cookies.get(cookie_name(settings, "session"), "")
    token_hash = opaque_hash(token)
    if token_hash is None:
        return None
    try:
        user = find_session_user(token_hash)
    except (DatabaseConfigError, SQLAlchemyError):
        raise auth_unavailable() from None
    if user is None:
        return None
    public_user = CurrentUser(id=user.id, email=user.email, display_name=user.display_name)
    return AuthenticatedSession(public_user, token_hash, csrf_token(token))


OptionalSession = Annotated[AuthenticatedSession | None, Depends(get_optional_session)]


def require_session(session: OptionalSession) -> AuthenticatedSession:
    if session is None:
        raise HTTPException(status_code=401, detail="Sign-in required.")
    return session


def require_same_origin(request: Request, settings: AuthSettings) -> None:
    if request.headers.get("origin") != settings.origin:
        raise HTTPException(status_code=403, detail="Request origin rejected.")


def verify_csrf(request: Request, settings: AuthSettings, session: AuthenticatedSession) -> None:
    require_same_origin(request, settings)
    supplied = request.headers.get("X-CSRF-Token", "")
    if not supplied.isascii() or not hmac.compare_digest(supplied, session.csrf):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")


def require_csrf_session(
    request: Request, settings: AuthConfig, session: Annotated[AuthenticatedSession, Depends(require_session)],
) -> AuthenticatedSession:
    verify_csrf(request, settings, session)
    return session
