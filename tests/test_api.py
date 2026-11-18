"""Tests for re-login and the login cooldown in MiWiFiClient.

They use a fake router and load api.py directly, so neither Home Assistant
nor a real router is needed. aiohttp is stubbed when it isn't installed.
Run with: python -m pytest tests
"""
import asyncio
import importlib.util
import json
import pathlib
import sys
import types

try:
    import aiohttp  # noqa: F401
except ImportError:
    _stub = types.ModuleType("aiohttp")
    _stub.ContentTypeError = type("ContentTypeError", (Exception,), {})
    sys.modules["aiohttp"] = _stub

_API_PATH = pathlib.Path(__file__).parents[1] / "custom_components/miwifi_cb0401v2/api.py"
_spec = importlib.util.spec_from_file_location("miwifi_api", _API_PATH)
api = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(api)

INVALID_TOKEN = {"code": 401, "msg": "Invalid token"}


class FakeResponse:
    def __init__(self, status, body):
        self.status = status
        self._body = json.dumps(body)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def text(self):
        return self._body

    async def json(self):
        return json.loads(self._body)


class FakeRouter:
    """Issues a new token on every login. Endpoints in `reject` always answer 401."""

    def __init__(self):
        self.valid_token = None
        self.logins = 0
        self.requests = []
        self.reject = set()

    def post(self, url, **kwargs):
        self.logins += 1
        self.valid_token = f"token{self.logins}"
        return FakeResponse(200, {"code": 0, "token": self.valid_token})

    def get(self, url, **kwargs):
        token = url.split("stok=")[1].split("/")[0]
        endpoint = url.split("/api/")[1]
        self.requests.append(endpoint)
        if token != self.valid_token or endpoint in self.reject:
            return FakeResponse(401, INVALID_TOKEN)
        if endpoint == "xqdtcustom/newstatus":
            return FakeResponse(200, {"code": 0, "hardware": {"mac": "00:00:00:00:00:01"}})
        if endpoint == "xqsystem/init_info":
            return FakeResponse(200, {"code": 0, "romversion": "3.5.39"})
        return FakeResponse(200, {"code": 0, "list": []})


def _client():
    router = FakeRouter()
    return router, api.MiWiFiClient("router", "admin", "pw", router)


def test_expired_token_triggers_one_relogin():
    async def run():
        router, client = _client()
        assert await client.login()
        router.valid_token = "dropped-by-router"
        assert await client.devicelist() == {"code": 0, "list": []}
        assert router.logins == 2

    asyncio.run(run())


def test_second_401_clears_token_and_starts_cooldown():
    async def run():
        router, client = _client()
        assert await client.login()
        router.reject.add("misystem/devicelist")

        assert await client.devicelist() is None
        assert router.logins == 2  # one re-login after the first 401
        assert client._token is None

        requests_before = len(router.requests)
        for _ in range(3):  # further polls during the cooldown
            assert await client.devicelist() is None
        assert router.logins == 2
        assert len(router.requests) == requests_before

        client._login_blocked_until = 0  # cooldown over
        router.reject.clear()
        assert await client.devicelist() == {"code": 0, "list": []}
        assert router.logins == 3

    asyncio.run(run())


def test_failed_login_starts_cooldown():
    async def run():
        router, client = _client()
        assert await client.login()
        attempts = []

        def rejected_login(url, **kwargs):
            attempts.append(url)
            return FakeResponse(200, {"code": 401, "msg": "wrong password"})

        router.post = rejected_login
        router.valid_token = "dropped-by-router"
        for _ in range(5):
            assert await client.devicelist() is None
        assert len(attempts) == 1

    asyncio.run(run())


def test_token_rejected_during_login_reports_failure():
    async def run():
        router, client = _client()
        router.reject.add("xqsystem/init_info")
        assert await client.login() is False
        assert client._token is None

    asyncio.run(run())
