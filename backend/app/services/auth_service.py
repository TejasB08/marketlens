import hmac
import logging
import re
import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import requests
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.requests_client import OAuth2Session
from joserfc import jwt
from joserfc.errors import ClaimError, JoseError
from joserfc.jwk import KeySet

from app.config import AuthSettings
from app.data import auth_store
from app.data.models import OAuthLoginAttempt


LOGIN_SECONDS = 10 * 60
SESSION_SECONDS = 7 * 24 * 60 * 60
AUTH_PATH = "/api/v1/auth"
CALLBACK_PATH = f"{AUTH_PATH}/google/callback"
GOOGLE_AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_KEYS = "https://www.googleapis.com/oauth2/v3/certs"
_OPAQUE_TOKEN = re.compile(r"[A-Za-z0-9_-]{43}")
logger = logging.getLogger("uvicorn.error.marketlens.auth")
_GOOGLE_ERROR_CODES = {
    "invalid_client", "invalid_grant", "invalid_request", "unauthorized_client",
    "unsupported_grant_type", "invalid_scope", "server_error", "temporarily_unavailable",
}
_LOGGABLE_CLAIMS = {"iss", "aud", "sub", "exp", "iat", "nbf", "nonce"}


class InvalidGoogleLogin(Exception):
    """The OAuth callback could not be authenticated."""

    def __init__(self, stage: str, reason: str) -> None:
        super().__init__("Google authentication failed.")
        self.stage = stage
        self.reason = reason


def opaque_hash(token: str | None) -> bytes | None:
    if token is None or _OPAQUE_TOKEN.fullmatch(token) is None:
        return None
    return sha256(token.encode("ascii")).digest()


def csrf_token(session_token: str) -> str:
    return hmac.digest(session_token.encode("ascii"), b"MarketLens CSRF v1", "sha256").hex()


def google_client(settings: AuthSettings) -> OAuth2Session:
    return OAuth2Session(
        settings.google_client_id, settings.google_client_secret,
        scope="openid email profile", redirect_uri=f"{settings.origin}{CALLBACK_PATH}",
        token_endpoint_auth_method="client_secret_post", code_challenge_method="S256",
    )


def start_google_login(settings: AuthSettings) -> tuple[str, str]:
    state, binding, nonce, verifier = (secrets.token_urlsafe(32) for _ in range(4))
    with google_client(settings) as client:
        redirect, _ = client.create_authorization_url(
            GOOGLE_AUTHORIZE, state=state, nonce=nonce, code_verifier=verifier,
        )
    auth_store.save_login_attempt(OAuthLoginAttempt(
        state_hash=sha256(state.encode()).digest(), browser_binding_hash=sha256(binding.encode()).digest(),
        nonce=nonce, pkce_verifier=verifier,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=LOGIN_SECONDS),
    ))
    return redirect, binding


def _log_audience_rejection(audience: object, client_id: str) -> None:
    if isinstance(audience, str):
        claim_type, audiences = "string", [audience]
    elif isinstance(audience, list):
        claim_type, audiences = "array", audience
    else:
        claim_type, audiences = ("missing" if audience is None else "other"), []
    logger.warning(
        "Google OAuth audience_check claim_type=%s client_match=%s untrusted_audience=%s invalid_element=%s",
        claim_type, client_id in audiences,
        any(isinstance(item, str) and item != client_id for item in audiences),
        any(not isinstance(item, str) for item in audiences),
    )


def verify_google_identity(settings: AuthSettings, code: str, nonce: str, verifier: str) -> dict:
    stage = "code_exchange"
    try:
        with google_client(settings) as client:
            response_token = client.fetch_token(
                GOOGLE_TOKEN, code=code, code_verifier=verifier, timeout=5, allow_redirects=False,
            )
        token = response_token.get("id_token")
        if not isinstance(token, str) or not token:
            raise InvalidGoogleLogin(stage, "missing_or_invalid_id_token")
        logger.info("Google OAuth stage=code_exchange outcome=success")

        stage = "signing_keys"
        with requests.get(GOOGLE_KEYS, timeout=5, allow_redirects=False) as response:
            response.raise_for_status()
            key_document = response.json()
        if not isinstance(key_document, dict) or not isinstance(key_document.get("keys"), list):
            raise InvalidGoogleLogin(stage, "invalid_response")
        keys = KeySet.import_key_set(key_document)
        logger.info("Google OAuth stage=signing_keys outcome=success")

        stage = "id_token_signature"
        claims = jwt.decode(token, keys, algorithms=["RS256"]).claims
        stage = "id_token_claims"
        jwt.JWTClaimsRegistry(
            leeway=30,
            iss={"essential": True, "values": ["https://accounts.google.com", "accounts.google.com"]},
            aud={"essential": True, "value": settings.google_client_id},
            sub={"essential": True}, exp={"essential": True}, iat={"essential": True},
            nonce={"essential": True},
        ).validate(claims)
        audience = claims["aud"]
        presenter = claims.get("azp")
        if claims["nonce"] != nonce:
            raise InvalidGoogleLogin(stage, "invalid_nonce")
        if not 0 < len(claims["sub"]) <= 255:
            raise InvalidGoogleLogin(stage, "invalid_sub")
        if presenter is not None and presenter != settings.google_client_id:
            raise InvalidGoogleLogin(stage, "invalid_azp")
        if isinstance(audience, list) and audience != [settings.google_client_id]:
            _log_audience_rejection(audience, settings.google_client_id)
            raise InvalidGoogleLogin(stage, "invalid_aud")
        logger.info("Google OAuth stage=id_token_validation outcome=success")
        return claims
    except OAuthError as exc:
        reason = exc.error if isinstance(exc.error, str) and exc.error in _GOOGLE_ERROR_CODES else "provider_error"
        raise InvalidGoogleLogin(stage, reason) from None
    except requests.Timeout:
        raise InvalidGoogleLogin(stage, "upstream_timeout") from None
    except requests.RequestException:
        raise InvalidGoogleLogin(stage, "upstream_request_failed") from None
    except ClaimError as exc:
        if stage == "id_token_claims" and "aud" in exc.claim.split(","):
            _log_audience_rejection(claims.get("aud"), settings.google_client_id)
        reason = f"invalid_{exc.claim}" if exc.claim in _LOGGABLE_CLAIMS else "invalid_claims"
        raise InvalidGoogleLogin(stage, reason) from None
    except JoseError:
        raise InvalidGoogleLogin(stage, "verification_failed") from None
    except (KeyError, ValueError, TypeError):
        raise InvalidGoogleLogin(stage, "invalid_response") from None


def complete_google_login(
    settings: AuthSettings, code: str, nonce: str, verifier: str, previous_session: str | None,
) -> str:
    claims = verify_google_identity(settings, code, nonce, verifier)
    email = claims.get("email")
    name = claims.get("name")
    token = secrets.token_urlsafe(32)
    auth_store.create_session(
        google_sub=claims["sub"],
        email=email if isinstance(email, str) and claims.get("email_verified") is True else None,
        display_name=name if isinstance(name, str) else None,
        token_hash=sha256(token.encode()).digest(),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=SESSION_SECONDS),
        previous_token_hash=opaque_hash(previous_session),
    )
    return token
