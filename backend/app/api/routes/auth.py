from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.dependencies.auth import (
    AuthConfig, OptionalSession, auth_unavailable, cookie_name, require_same_origin, verify_csrf,
)
from app.config import AuthSettings, DatabaseConfigError
from app.data import auth_store
from app.schemas.auth_schema import SessionResponse
from app.services.auth_service import (
    AUTH_PATH, CALLBACK_PATH, LOGIN_SECONDS, SESSION_SECONDS, InvalidGoogleLogin,
    complete_google_login, csrf_token, logger, opaque_hash, start_google_login,
)


router = APIRouter(prefix="/auth", tags=["authentication"])


class AuthResponseMiddleware:
    """Keep OAuth query parameters out of the ASGI access log and auth responses out of caches."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = scope.get("path", "")
        if scope["type"] != "http" or not path.startswith(f"{AUTH_PATH}/"):
            await self.app(scope, receive, send)
            return

        request_scope = scope.copy()
        scope["query_string"] = b""
        if path != CALLBACK_PATH:
            request_scope["query_string"] = b""

        async def send_private(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Cache-Control"] = "no-store"
                headers["Referrer-Policy"] = "no-referrer"
            await send(message)

        await self.app(request_scope, receive, send_private)


def _set_cookie(
    response: Response, settings: AuthSettings, kind: str, value: str, max_age: int,
) -> None:
    response.set_cookie(cookie_name(settings, kind), value, max_age=max_age, path="/",
                        secure=settings.secure_cookies, httponly=kind != "csrf", samesite="lax")


def _clear_cookie(response: Response, settings: AuthSettings, kind: str) -> None:
    response.delete_cookie(cookie_name(settings, kind), path="/", secure=settings.secure_cookies,
                           httponly=kind != "csrf", samesite="lax")


@router.get("/google/login", status_code=303, response_class=RedirectResponse)
def google_login(settings: AuthConfig) -> RedirectResponse:
    try:
        location, binding = start_google_login(settings)
    except (DatabaseConfigError, SQLAlchemyError, ValueError):
        logger.warning("Google OAuth stage=attempt_creation outcome=failed")
        raise auth_unavailable() from None
    logger.info("Google OAuth stage=attempt_creation outcome=success")
    response = RedirectResponse(location, status_code=303)
    _set_cookie(response, settings, "oauth", binding, LOGIN_SECONDS)
    return response


@router.get("/google/callback", status_code=303, response_class=RedirectResponse)
def google_callback(request: Request, settings: AuthConfig) -> RedirectResponse:
    failure = RedirectResponse(f"{settings.origin}/?auth=failed", status_code=303)
    states = request.query_params.getlist("state")
    state_hash = opaque_hash(states[0]) if len(states) == 1 else None
    binding_hash = opaque_hash(request.cookies.get(cookie_name(settings, "oauth")))
    if state_hash is None or binding_hash is None:
        reason = "invalid_state" if state_hash is None else "invalid_browser_binding"
        logger.warning("Google OAuth stage=callback_input outcome=failed reason=%s", reason)
        return failure

    stage = "attempt_consumption"
    try:
        attempt = auth_store.consume_login_attempt(state_hash, binding_hash)
        if attempt is None:
            logger.warning("Google OAuth stage=attempt_consumption outcome=failed reason=no_live_match")
            return failure
        logger.info("Google OAuth stage=attempt_consumption outcome=success")
        _clear_cookie(failure, settings, "oauth")
        codes = request.query_params.getlist("code")
        if "error" in request.query_params:
            reason = "access_denied" if request.query_params["error"] == "access_denied" else "provider_error"
            logger.warning("Google OAuth stage=authorization_response outcome=failed reason=%s", reason)
            return failure
        if len(codes) != 1 or not 0 < len(codes[0]) <= 4096:
            logger.warning("Google OAuth stage=authorization_response outcome=failed reason=invalid_code")
            return failure
        nonce, verifier = attempt
        stage = "session_persistence"
        token = complete_google_login(
            settings, codes[0], nonce, verifier, request.cookies.get(cookie_name(settings, "session")),
        )
    except InvalidGoogleLogin as exc:
        logger.warning("Google OAuth stage=%s outcome=failed reason=%s", exc.stage, exc.reason)
        return failure
    except (DatabaseConfigError, SQLAlchemyError):
        logger.warning("Google OAuth stage=%s outcome=failed reason=database_unavailable", stage)
        raise auth_unavailable() from None

    logger.info("Google OAuth stage=session_persistence outcome=success")
    response = RedirectResponse(f"{settings.origin}/", status_code=303)
    _clear_cookie(response, settings, "oauth")
    _set_cookie(response, settings, "session", token, SESSION_SECONDS)
    _set_cookie(response, settings, "csrf", csrf_token(token), SESSION_SECONDS)
    return response


@router.get("/session", response_model=SessionResponse)
def current_session(request: Request, response: Response, settings: AuthConfig,
                    session: OptionalSession) -> SessionResponse:
    if session is None:
        if cookie_name(settings, "session") in request.cookies:
            _clear_cookie(response, settings, "session")
            _clear_cookie(response, settings, "csrf")
        return SessionResponse(user=None)
    if request.cookies.get(cookie_name(settings, "csrf")) != session.csrf:
        _set_cookie(response, settings, "csrf", session.csrf, SESSION_SECONDS)
    return SessionResponse(user=session.user)


@router.post("/logout", status_code=204, response_class=Response)
def logout(request: Request, settings: AuthConfig, session: OptionalSession) -> Response:
    if session is None:
        require_same_origin(request, settings)
    else:
        verify_csrf(request, settings, session)
        try:
            auth_store.revoke_session(session.token_hash)
        except (DatabaseConfigError, SQLAlchemyError):
            raise auth_unavailable() from None
    response = Response(status_code=204)
    _clear_cookie(response, settings, "session")
    _clear_cookie(response, settings, "csrf")
    _clear_cookie(response, settings, "oauth")
    return response
