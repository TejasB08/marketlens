import asyncio
import json
import secrets
import time
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlencode, urlsplit
from unittest.mock import patch

from joserfc import jwt
from joserfc.jwk import RSAKey
from requests import Response
from sqlalchemy import func, select, update
from sqlalchemy.orm import sessionmaker
from test_database import PostgreSQLTestCase, digest

from app.api.dependencies.auth import get_auth_settings
from app.config import AuthSettings
from app.data import auth_store
from app.data.models import AuthSession, OAuthLoginAttempt, User
from app.main import app
from app.services.auth_service import AUTH_PATH, CALLBACK_PATH, GOOGLE_KEYS, GOOGLE_TOKEN, SESSION_SECONDS


class AuthTests(PostgreSQLTestCase):
    origin = "https://marketlens.example.test"
    client_id = "fixture-client-id"
    subject = "google-subject-1"
    binding_cookie = "__Host-marketlens_oauth"
    session_cookie = "__Host-marketlens_session"
    csrf_cookie = "__Host-marketlens_csrf"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.key = RSAKey.generate_key(2048, parameters={"kid": "fixture-key"}, private=True)

    def setUp(self):
        super().setUp()
        factory = sessionmaker(bind=self.connection, join_transaction_mode="create_savepoint")
        self.enterContext(patch.object(auth_store, "get_session_factory", return_value=factory))
        self.enterContext(patch.dict(app.dependency_overrides, {
            get_auth_settings: lambda: AuthSettings(self.origin, self.client_id, "fixture-client-secret")
        }))
        self.enterContext(patch("requests.sessions.Session.send", side_effect=self.mock_google))
        self.google_calls = []
        self.claim_overrides = {}
        self.invalid_signature = False
        self.token_error = None

    def mock_google(self, request, **kwargs):
        self.assertEqual(kwargs["timeout"], 5)
        self.google_calls.append(request.url)
        if request.url == GOOGLE_TOKEN:
            body = parse_qs(request.body)
            self.assertEqual(request.method, "POST")
            self.assertEqual(body["grant_type"], ["authorization_code"])
            self.assertEqual(body["code"], ["test-google-code"])
            self.assertEqual(body["redirect_uri"], [self.origin + CALLBACK_PATH])
            self.assertEqual(body["code_verifier"], [self.verifier])
            self.assertEqual(body["client_id"], [self.client_id])
            self.assertEqual(body["client_secret"], ["fixture-client-secret"])
            now = int(time.time())
            claims = dict(
                sub=self.subject, aud=self.client_id, iss="https://accounts.google.com",
                nonce=self.nonce, iat=now, exp=now + 300, name="Fixture Name",
                email="verified@example.test", email_verified=True, azp=self.client_id,
            ) | self.claim_overrides
            token = jwt.encode({"alg": "RS256", "kid": "fixture-key"}, claims, self.key)
            if self.invalid_signature:
                prefix, signature = token.rsplit(".", 1)
                first = "A" if signature[0] != "A" else "B"
                token = f"{prefix}.{first}{signature[1:]}"
            payload = {
                "id_token": token, "access_token": "mock-google-access-token", "token_type": "Bearer",
                "expires_in": 3599, "scope": "https://www.googleapis.com/auth/userinfo.email openid https://www.googleapis.com/auth/userinfo.profile",
            }
            if self.token_error is not None:
                payload = {"error": self.token_error, "error_description": "upstream-sensitive-detail"}
        elif request.url == GOOGLE_KEYS:
            self.assertEqual(request.method, "GET")
            payload = {"keys": [self.key.as_dict(private=False)]}
        else:
            self.fail("Unexpected upstream request.")
        response = Response()
        response.status_code = 400 if request.url == GOOGLE_TOKEN and self.token_error else 200
        response._content = json.dumps(payload).encode()
        response.headers["Content-Type"] = "application/json"
        response.request = request
        return response

    def request(self, method, path, *, query=None, cookies=None, headers=None):
        async def send_request():
            messages = []
            incoming = dict(headers or {})
            if cookies:
                incoming["cookie"] = "; ".join(f"{key}={value}" for key, value in cookies.items())
            scope = {
                "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": method,
                "scheme": "https", "path": path, "raw_path": path.encode(),
                "query_string": urlencode(query or {}).encode(),
                "headers": [(name.lower().encode(), value.encode()) for name, value in incoming.items()],
                "client": ("127.0.0.1", 9999), "server": ("marketlens.example.test", 443),
            }

            async def receive():
                return {"type": "http.request", "body": b"", "more_body": False}

            async def send(message):
                messages.append(message)

            await app(scope, receive, send)
            if path.startswith(AUTH_PATH):
                self.assertEqual(scope["query_string"], b"")
            return messages

        start, *body_events = asyncio.run(send_request())
        response_headers = {key.decode(): value.decode() for key, value in start["headers"]}
        response_cookies = SimpleCookie()
        for key, value in start["headers"]:
            if key == b"set-cookie":
                response_cookies.load(value.decode())
        body = b"".join(event.get("body", b"") for event in body_events)
        if path.startswith(AUTH_PATH):
            self.assertEqual(response_headers["cache-control"], "no-store")
            self.assertEqual(response_headers["referrer-policy"], "no-referrer")
        return start["status"], response_headers, response_cookies, body

    def start_login(self):
        status, headers, cookies, _ = self.request("GET", AUTH_PATH + "/google/login")
        self.assertEqual(status, 303)
        url = urlsplit(headers["location"])
        self.assertEqual(url.netloc, "accounts.google.com")
        params = parse_qs(url.query)
        self.assertEqual(params["response_type"], ["code"])
        self.assertEqual(params["client_id"], [self.client_id])
        self.assertEqual(params["code_challenge_method"], ["S256"])
        self.assertEqual(params["redirect_uri"], [self.origin + CALLBACK_PATH])
        self.assertNotIn("client_secret", params)
        binding = cookies[self.binding_cookie]
        self.assertTrue(binding["secure"] and binding["httponly"])
        self.assertEqual(binding["max-age"], "600")
        self.assertEqual(binding["samesite"], "lax")
        state = params["state"][0]
        attempt = self.connection.execute(select(OAuthLoginAttempt.__table__).where(
            OAuthLoginAttempt.state_hash == digest(state)
        )).one()
        self.nonce = params["nonce"][0]
        self.verifier = attempt.pkce_verifier
        self.assertEqual(params["code_challenge"], [
            urlsafe_b64encode(digest(self.verifier)).decode().rstrip("=")
        ])
        self.assertEqual(attempt.browser_binding_hash, digest(binding.value))
        return state, binding.value

    def callback(self, state, binding, **extra_cookies):
        return self.request("GET", CALLBACK_PATH, query={"code": "test-google-code", "state": state},
                            cookies={self.binding_cookie: binding, **extra_cookies})

    def sign_in(self, **extra_cookies):
        state, binding = self.start_login()
        status, headers, cookies, body = self.callback(state, binding, **extra_cookies)
        self.assertEqual((status, headers["location"], body), (303, self.origin + "/", b""))
        self.assertEqual(cookies[self.binding_cookie]["max-age"], "0")
        return {name: cookies[name].value for name in (self.session_cookie, self.csrf_cookie)}, cookies

    def current(self, cookies):
        status, _, _, body = self.request("GET", AUTH_PATH + "/session", cookies=cookies)
        self.assertEqual(status, 200)
        return json.loads(body)["user"]

    def test_successful_authentication_with_hashed_session_and_expiry(self):
        jar, cookies = self.sign_in()
        session_cookie = cookies[self.session_cookie]
        self.assertTrue(session_cookie["httponly"] and session_cookie["secure"])
        self.assertEqual(session_cookie["samesite"], "lax")
        self.assertFalse(session_cookie["domain"])
        self.assertEqual(session_cookie["max-age"], str(SESSION_SECONDS))
        self.assertFalse(cookies[self.csrf_cookie]["httponly"])
        self.assertEqual(self.google_calls, [GOOGLE_TOKEN, GOOGLE_KEYS])
        row = self.connection.execute(select(AuthSession.__table__)).one()
        self.assertEqual(row.token_hash, digest(jar[self.session_cookie]))
        self.assertAlmostEqual((row.expires_at - datetime.now(timezone.utc)).total_seconds(), SESSION_SECONDS, delta=5)
        self.assertEqual(self.current(jar), {"id": str(row.user_id), "email": "verified@example.test",
                                             "display_name": "Fixture Name"})
        self.assertIsNone(self.current({}))

    def test_login_reuses_stable_subject_and_rotates_session(self):
        first, _ = self.sign_in()
        user_id = self.current(first)["id"]
        self.claim_overrides["email"] = "updated@example.test"
        second, _ = self.sign_in(**first)
        self.assertNotEqual(first[self.session_cookie], second[self.session_cookie])
        self.assertIsNone(self.current(first))
        self.assertEqual(self.current(second)["id"], user_id)
        self.assertEqual(self.current(second)["email"], "updated@example.test")
        self.assertEqual(self.connection.scalar(select(func.count()).select_from(User)), 1)

    def assert_failed_callback(self, state, binding):
        status, headers, cookies, _ = self.callback(state, binding)
        self.assertEqual((status, headers["location"]), (303, self.origin + "/?auth=failed"))
        self.assertNotIn(self.session_cookie, cookies)

    def test_invalid_state_and_browser_binding_cannot_consume_valid_attempt(self):
        state, binding = self.start_login()
        self.assert_failed_callback(secrets.token_urlsafe(32), binding)
        self.assert_failed_callback(state, secrets.token_urlsafe(32))
        self.assertEqual(self.google_calls, [])
        self.assertEqual(self.callback(state, binding)[1]["location"], self.origin + "/")

    def test_expired_attempt_is_rejected_without_contacting_google(self):
        state, binding = self.start_login()
        self.connection.execute(update(OAuthLoginAttempt).values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)))
        self.assert_failed_callback(state, binding)
        self.assertEqual(self.google_calls, [])

    def test_replay_is_rejected(self):
        state, binding = self.start_login()
        self.assertEqual(self.callback(state, binding)[1]["location"], self.origin + "/")
        self.assert_failed_callback(state, binding)
        self.assertEqual(self.google_calls, [GOOGLE_TOKEN, GOOGLE_KEYS])

    def test_invalid_nonce_and_audience_cannot_create_session(self):
        for claims in ({"nonce": "invalid"}, {"aud": "another-client"}, {"iss": "https://another-issuer.test"},
                       {"exp": int(time.time()) - 60}):
            with self.subTest(claims=claims):
                self.claim_overrides = claims
                state, binding = self.start_login()
                self.assert_failed_callback(state, binding)
        self.assertEqual(self.connection.scalar(select(func.count()).select_from(AuthSession)), 0)

    def test_accepts_singleton_audience_array_for_configured_client(self):
        self.claim_overrides["aud"] = [self.client_id]
        jar, _ = self.sign_in()
        self.assertIsNotNone(self.current(jar))

    def test_audience_rejections_are_logged_without_client_identifiers(self):
        other_client = "fixture-other-client"
        cases = (
            (other_client, "string", False, True, False),
            ([other_client], "array", False, True, False),
            ([self.client_id, other_client], "array", True, True, False),
            ([self.client_id, 123], "array", True, False, True),
            ([], "array", False, False, False),
            (None, "missing", False, False, False),
        )
        for audience, claim_type, client_match, untrusted, invalid_element in cases:
            with self.subTest(claim_type=claim_type, client_match=client_match):
                self.claim_overrides["aud"] = audience
                state, binding = self.start_login()
                with self.assertLogs("uvicorn.error.marketlens.auth", level="WARNING") as logs:
                    self.assert_failed_callback(state, binding)
                text = "\n".join(logs.output)
                self.assertIn("stage=id_token_claims outcome=failed reason=invalid_aud", text)
                self.assertIn(
                    f"claim_type={claim_type} client_match={client_match} "
                    f"untrusted_audience={untrusted} invalid_element={invalid_element}", text,
                )
                self.assertNotIn(self.client_id, text)
                self.assertNotIn(other_client, text)
        self.assertEqual(self.connection.scalar(select(func.count()).select_from(User)), 0)
        self.assertEqual(self.connection.scalar(select(func.count()).select_from(AuthSession)), 0)

    def test_rejects_another_authorized_presenter_with_matching_audience(self):
        self.claim_overrides["azp"] = "fixture-other-client"
        state, binding = self.start_login()
        with self.assertLogs("uvicorn.error.marketlens.auth", level="WARNING") as logs:
            self.assert_failed_callback(state, binding)
        self.assertIn("reason=invalid_azp", "\n".join(logs.output))
        self.assertEqual(self.connection.scalar(select(func.count()).select_from(AuthSession)), 0)

    def test_google_exchange_failure_is_sanitized_and_consumes_attempt(self):
        self.token_error = "invalid_grant"
        state, binding = self.start_login()
        with self.assertLogs("uvicorn.error.marketlens.auth", level="INFO") as logs:
            self.assert_failed_callback(state, binding)
        log = "\n".join(logs.output)
        self.assertIn("stage=attempt_consumption outcome=success", log)
        self.assertIn("stage=code_exchange outcome=failed reason=invalid_grant", log)
        for sensitive in (state, binding, "test-google-code", "upstream-sensitive-detail", "fixture-client-secret"):
            self.assertNotIn(sensitive, log)
        for model in (OAuthLoginAttempt, User, AuthSession):
            self.assertEqual(self.connection.scalar(select(func.count()).select_from(model)), 0)

    def test_invalid_signature_cannot_create_session(self):
        self.invalid_signature = True
        state, binding = self.start_login()
        self.assert_failed_callback(state, binding)
        self.assertEqual(self.connection.scalar(select(func.count()).select_from(AuthSession)), 0)

    def test_google_denial_consumes_attempt_and_clears_binding(self):
        state, binding = self.start_login()
        status, headers, cookies, _ = self.request(
            "GET", CALLBACK_PATH, query={"error": "access_denied", "state": state},
            cookies={self.binding_cookie: binding},
        )
        self.assertEqual((status, headers["location"]), (303, self.origin + "/?auth=failed"))
        self.assertEqual(cookies[self.binding_cookie]["max-age"], "0")
        self.assert_failed_callback(state, binding)
        self.assertEqual(self.google_calls, [])

    def test_expired_session_returns_guest_and_clears_cookies(self):
        jar, _ = self.sign_in()
        self.connection.execute(update(AuthSession).values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)))
        status, _, cookies, body = self.request("GET", AUTH_PATH + "/session", cookies=jar)
        self.assertEqual((status, json.loads(body)), (200, {"user": None}))
        self.assertEqual(cookies[self.session_cookie]["max-age"], "0")
        self.assertEqual(cookies[self.csrf_cookie]["max-age"], "0")

    def test_logout_requires_origin_and_csrf_then_revokes_session(self):
        jar, _ = self.sign_in()
        endpoint = AUTH_PATH + "/logout"
        valid = {"Origin": self.origin, "X-CSRF-Token": jar[self.csrf_cookie]}
        for headers in ({}, {"Origin": self.origin}, valid | {"Origin": "https://other.example.test"},
                        valid | {"X-CSRF-Token": "wrong"}):
            self.assertEqual(self.request("POST", endpoint, cookies=jar, headers=headers)[0], 403)
        self.assertIsNotNone(self.current(jar))
        status, _, cookies, body = self.request("POST", endpoint, cookies=jar, headers=valid)
        self.assertEqual((status, body), (204, b""))
        self.assertEqual(cookies[self.session_cookie]["max-age"], "0")
        self.assertIsNotNone(self.connection.scalar(select(AuthSession.revoked_at)))
        self.assertIsNone(self.current(jar))

    def test_guest_can_use_public_api(self):
        self.assertEqual(self.request("GET", "/")[0], 200)
        status, _, _, body = self.request("GET", "/api/v1/watchlist")
        self.assertEqual((status, json.loads(body)), (200, {"count": 0, "tickers": []}))
