"""Tests for API key handling.

Covers ``resolve_api_key`` precedence, ``lmConfig --api-key`` /
``--remove-api-key`` / ``--show``, the authentication prompt in ``cmd_init``,
the error classification in ``_fetch_with_key``, and config file permissions.

``cmd_init`` prompts via ``input()`` (and ``confirm()``) and, for the key,
via ``getpass.getpass()``; both are mocked so every interaction is
deterministic.
"""

import json
import sys

import httpx2
import pytest

from lemonpie.cli import config_cmd
from lemonpie.cli.config_cmd import _fetch_with_key, cmd_init
from lemonpie.config import resolve_api_key, save_config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_input(responses):
    it = iter(responses)
    return lambda _prompt="": next(it)


def _read_cfg(isolated_dirs):
    return json.loads(isolated_dirs["config_file"].read_text(encoding="utf-8"))


def _set_getpass(monkeypatch, value):
    monkeypatch.setattr("getpass.getpass", lambda _prompt="": value)


def _forbid_getpass(monkeypatch):
    def _boom(_prompt=""):
        raise AssertionError("getpass must not be called")

    monkeypatch.setattr("getpass.getpass", _boom)


def _auth_server(monkeypatch, good_key, models):
    """Server that answers 401 unless called with *good_key*. Returns call log."""
    calls = []

    def fake(_server, _key=None):
        calls.append(_key)
        if _key == good_key:
            return models, None, False
        return [], "Server requires authentication", True

    monkeypatch.setattr("lemonpie.cli.config_cmd._fetch_with_key", fake)
    return calls


# Input prefix for cmd_init: Ollama, local, default URL
_WIZARD_START = ["2", "y", "1"]

# ---------------------------------------------------------------------------
# resolve_api_key
# ---------------------------------------------------------------------------


class TestResolveApiKey:
    def test_env_overrides_config(self, monkeypatch):
        monkeypatch.setenv("LEMONPIE_API_KEY", "sk-env")
        assert resolve_api_key({"api_key": "sk-cfg"}) == "sk-env"

    def test_falls_back_to_config(self):
        assert resolve_api_key({"api_key": "sk-cfg"}) == "sk-cfg"

    def test_empty_env_falls_back_to_config(self, monkeypatch):
        monkeypatch.setenv("LEMONPIE_API_KEY", "")
        assert resolve_api_key({"api_key": "sk-cfg"}) == "sk-cfg"

    def test_nothing_set(self):
        assert resolve_api_key({"api_key": None}) is None
        assert resolve_api_key({}) is None


# ---------------------------------------------------------------------------
# lmConfig --api-key / --remove-api-key / --show
# ---------------------------------------------------------------------------


class TestApiKeyCommands:
    def _run(self, monkeypatch, *args):
        monkeypatch.setattr(sys, "argv", ["lmConfig", *args])
        return config_cmd.main()

    def test_set_key_from_argument(self, isolated_dirs, monkeypatch):
        assert self._run(monkeypatch, "--api-key", "sk-1") == 0
        assert _read_cfg(isolated_dirs)["api_key"] == "sk-1"

    def test_set_key_prompts_when_no_value(self, isolated_dirs, monkeypatch):
        _set_getpass(monkeypatch, "  sk-prompted  ")
        assert self._run(monkeypatch, "--api-key") == 0
        assert _read_cfg(isolated_dirs)["api_key"] == "sk-prompted"

    def test_empty_prompt_is_rejected_and_config_unchanged(
        self, write_cfg, isolated_dirs, monkeypatch
    ):
        _set_getpass(monkeypatch, "")
        assert self._run(monkeypatch, "--api-key") == 2
        assert _read_cfg(isolated_dirs)["api_key"] is None

    def test_empty_argument_is_rejected(self, write_cfg, isolated_dirs, monkeypatch):
        assert self._run(monkeypatch, "--api-key", "") == 2
        assert _read_cfg(isolated_dirs)["api_key"] is None

    def test_remove_key(self, write_cfg, isolated_dirs, monkeypatch):
        save_config({**write_cfg, "api_key": "sk-old"})
        assert self._run(monkeypatch, "--remove-api-key") == 0
        assert _read_cfg(isolated_dirs)["api_key"] is None

    def test_env_override_warning(self, isolated_dirs, monkeypatch, capsys):
        monkeypatch.setenv("LEMONPIE_API_KEY", "sk-env")
        assert self._run(monkeypatch, "--api-key", "sk-1") == 0
        assert "LEMONPIE_API_KEY" in capsys.readouterr().out

    def test_show_masks_key(self, write_cfg, isolated_dirs, monkeypatch, capsys):
        secret = "sk-secret-value-1234"
        save_config({**write_cfg, "api_key": secret})
        assert self._run(monkeypatch, "--show") == 0
        out = capsys.readouterr().out
        assert secret not in out
        assert "****1234" in out


# ---------------------------------------------------------------------------
# Config file permissions
# ---------------------------------------------------------------------------


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits")
def test_config_file_is_owner_only(isolated_dirs):
    save_config({"api_key": "sk-1"})
    assert isolated_dirs["config_file"].stat().st_mode & 0o777 == 0o600


# ---------------------------------------------------------------------------
# cmd_init authentication prompt
# ---------------------------------------------------------------------------


class TestCmdInitAuth:
    def test_key_accepted_is_saved(self, isolated_dirs, monkeypatch):
        calls = _auth_server(monkeypatch, "sk-good", ["qwen2.5-coder:3b"])
        _set_getpass(monkeypatch, "sk-good")
        monkeypatch.setattr(
            "builtins.input", _make_input([*_WIZARD_START, ""])  # skip selection
        )
        assert cmd_init() == 0

        assert _read_cfg(isolated_dirs)["api_key"] == "sk-good"
        assert calls == [None, "sk-good"]

    def test_key_rejected_continue_does_not_save_key(self, isolated_dirs, monkeypatch):
        _auth_server(monkeypatch, "sk-good", [])
        _set_getpass(monkeypatch, "sk-bad")
        monkeypatch.setattr(
            "builtins.input",
            _make_input([*_WIZARD_START, "y", "n"]),  # continue; no manual model
        )
        assert cmd_init() == 0
        assert _read_cfg(isolated_dirs)["api_key"] is None

    def test_key_rejected_abort(self, isolated_dirs, monkeypatch):
        _auth_server(monkeypatch, "sk-good", [])
        _set_getpass(monkeypatch, "sk-bad")
        monkeypatch.setattr("builtins.input", _make_input([*_WIZARD_START, "n"]))
        assert cmd_init() == 1
        assert not isolated_dirs["config_file"].exists()

    def test_key_skipped_goes_to_continue_prompt_without_retry(
        self, isolated_dirs, monkeypatch
    ):
        calls = _auth_server(monkeypatch, "sk-good", [])
        _set_getpass(monkeypatch, "")
        monkeypatch.setattr("builtins.input", _make_input([*_WIZARD_START, "n"]))
        assert cmd_init() == 1
        assert calls == [None]

    def test_env_key_used_for_probe_but_not_saved(self, isolated_dirs, monkeypatch):
        monkeypatch.setenv("LEMONPIE_API_KEY", "sk-env")
        calls = _auth_server(monkeypatch, "sk-env", ["qwen2.5-coder:3b"])
        _forbid_getpass(monkeypatch)
        monkeypatch.setattr("builtins.input", _make_input([*_WIZARD_START, ""]))
        assert cmd_init() == 0

        assert calls == ["sk-env"]
        assert _read_cfg(isolated_dirs)["api_key"] is None

    def test_non_auth_failure_does_not_prompt_for_key(self, isolated_dirs, monkeypatch):
        monkeypatch.setattr(
            "lemonpie.cli.config_cmd._fetch_with_key",
            lambda _server, _key=None: ([], "Connection refused", False),
        )
        _forbid_getpass(monkeypatch)
        monkeypatch.setattr("builtins.input", _make_input([*_WIZARD_START, "n"]))
        assert cmd_init() == 1

    def test_force_never_prompts_for_key(self, isolated_dirs, monkeypatch):
        _forbid_getpass(monkeypatch)
        monkeypatch.setattr(
            "builtins.input", _make_input([*_WIZARD_START, "n"])  # no manual model
        )
        assert cmd_init(force=True) == 0
        assert _read_cfg(isolated_dirs)["api_key"] is None


# ---------------------------------------------------------------------------
# _fetch_with_key classification
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, status=200, payload=None, json_error=None):
        self.status_code = status
        self._payload = payload
        self._json_error = json_error

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx2.Request("GET", "http://test/v1/models")
            response = httpx2.Response(self.status_code, request=request)
            raise httpx2.HTTPStatusError(
                "error", request=request, response=response
            )

    def json(self):
        if self._json_error:
            raise self._json_error
        return self._payload


class _FakeClient:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_exc_info):
        self.closed = True

    def get(self, _path):
        if self._exc:
            raise self._exc
        return self._response


def _install(monkeypatch, client):
    monkeypatch.setattr(config_cmd, "build_client", lambda *a, **k: client)


class TestFetchWithKey:
    def test_success(self, monkeypatch):
        client = _FakeClient(_FakeResponse(payload={"data": [{"id": "a"}, {"id": "b"}]}))
        _install(monkeypatch, client)
        assert _fetch_with_key("http://test") == (["a", "b"], None, False)
        assert client.closed

    @pytest.mark.parametrize("status", [401, 403])
    def test_auth_statuses_flag_auth_err(self, monkeypatch, status):
        client = _FakeClient(_FakeResponse(status=status))
        _install(monkeypatch, client)
        models, err, auth_err = _fetch_with_key("http://test")
        assert models == [] and err and auth_err is True
        assert client.closed

    def test_other_status_is_not_auth_err(self, monkeypatch):
        _install(monkeypatch, _FakeClient(_FakeResponse(status=500)))
        _models, err, auth_err = _fetch_with_key("http://test")
        assert "500" in err and auth_err is False

    @pytest.mark.parametrize(
        "exc",
        [
            httpx2.ConnectError("[Errno 111] Connection refused"),
            httpx2.ConnectTimeout("timed out"),
            httpx2.ReadError("connection reset"),
        ],
    )
    def test_transport_errors_are_reported_not_raised(self, monkeypatch, exc):
        client = _FakeClient(exc=exc)
        _install(monkeypatch, client)
        models, err, auth_err = _fetch_with_key("http://test")
        assert models == [] and err and auth_err is False
        assert client.closed

    @pytest.mark.parametrize(
        "response",
        [
            _FakeResponse(payload=["not", "a", "dict"]),
            _FakeResponse(payload={"data": [{"no_id": 1}]}),
            _FakeResponse(json_error=json.JSONDecodeError("bad", "", 0)),
        ],
    )
    def test_malformed_body_is_reported_not_raised(self, monkeypatch, response):
        _install(monkeypatch, _FakeClient(response))
        models, err, auth_err = _fetch_with_key("http://test")
        assert models == [] and "Invalid response" in err and auth_err is False
