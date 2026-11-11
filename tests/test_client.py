"""Tests for lemonpie.client — build_client, stream_chat, and error resolution."""

import json
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import httpx
import pytest

from lemonpie.client import build_client, resolve_error, stream_chat

SERVER = "http://localhost:9931"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sse_lines(chunks):
    """Build an SSE line list from a list of content strings."""
    lines = [
        f'data: {json.dumps({"choices": [{"delta": {"content": c}}]})}'
        for c in chunks
    ]
    lines.append("data: [DONE]")
    return lines


def _mock_stream(lines):
    """Return a context-manager-compatible replacement for client.stream()."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.iter_lines.return_value = iter(lines)

    @contextmanager
    def _cm(*args, **kwargs):
        yield mock_response

    return _cm


# ---------------------------------------------------------------------------
# build_client
# ---------------------------------------------------------------------------

class TestBuildClient:
    def test_returns_httpx_client(self):
        client = build_client(SERVER, httpx.Timeout(5.0))
        assert isinstance(client, httpx.Client)

    def test_sets_base_url(self):
        client = build_client(SERVER, httpx.Timeout(5.0))
        assert SERVER in str(client.base_url)

    def test_no_auth_header_without_api_key(self):
        client = build_client(SERVER, httpx.Timeout(5.0))
        assert "authorization" not in client.headers

    def test_sets_auth_header_with_api_key(self):
        client = build_client(SERVER, httpx.Timeout(5.0), api_key="sk-test")
        assert client.headers["authorization"] == "Bearer sk-test"


# ---------------------------------------------------------------------------
# stream_chat
# ---------------------------------------------------------------------------

class TestStreamChat:
    def _client(self):
        return httpx.Client(base_url=SERVER)

    def test_yields_content_chunks(self):
        client = self._client()
        messages = [{"role": "user", "content": "hi"}]
        with patch.object(client, "stream", new=_mock_stream(_make_sse_lines(["Hello", ", ", "world"]))):
            result = list(stream_chat(client, "qwen", messages))
        assert result == ["Hello", ", ", "world"]

    def test_strips_ts_from_messages(self):
        client = self._client()
        messages = [{"role": "user", "content": "hi", "ts": "2026-01-01"}]
        captured = {}

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = iter(["data: [DONE]"])

        @contextmanager
        def capturing_stream(*args, **kwargs):
            captured.update(kwargs)
            yield mock_response

        with patch.object(client, "stream", new=capturing_stream):
            list(stream_chat(client, "qwen", messages))

        sent = captured["json"]["messages"]
        assert sent == [{"role": "user", "content": "hi"}]

    def test_skips_empty_content(self):
        client = self._client()
        messages = [{"role": "user", "content": "hi"}]
        lines = [
            'data: {"choices": [{"delta": {"content": ""}}]}',
            'data: {"choices": [{"delta": {}}]}',
            'data: {"choices": [{"delta": {"content": "real"}}]}',
            "data: [DONE]",
        ]
        with patch.object(client, "stream", new=_mock_stream(lines)):
            result = list(stream_chat(client, "qwen", messages))
        assert result == ["real"]

    def test_stops_at_done_sentinel(self):
        client = self._client()
        messages = [{"role": "user", "content": "hi"}]
        lines = [
            'data: {"choices": [{"delta": {"content": "before"}}]}',
            "data: [DONE]",
            'data: {"choices": [{"delta": {"content": "after"}}]}',
        ]
        with patch.object(client, "stream", new=_mock_stream(lines)):
            result = list(stream_chat(client, "qwen", messages))
        assert result == ["before"]

    def test_skips_non_data_lines(self):
        client = self._client()
        messages = [{"role": "user", "content": "hi"}]
        lines = [
            ": keep-alive",
            "",
            'data: {"choices": [{"delta": {"content": "hi"}}]}',
            "data: [DONE]",
        ]
        with patch.object(client, "stream", new=_mock_stream(lines)):
            result = list(stream_chat(client, "qwen", messages))
        assert result == ["hi"]

    def test_skips_malformed_json(self):
        client = self._client()
        messages = [{"role": "user", "content": "hi"}]
        lines = [
            "data: {not valid json",
            'data: {"choices": [{"delta": {"content": "ok"}}]}',
            "data: [DONE]",
        ]
        with patch.object(client, "stream", new=_mock_stream(lines)):
            result = list(stream_chat(client, "qwen", messages))
        assert result == ["ok"]


# ---------------------------------------------------------------------------
# resolve_error
# ---------------------------------------------------------------------------

class TestResolveError:
    def test_connect_timeout(self):
        exc = httpx.ConnectTimeout("timed out")
        msg, hint = resolve_error(exc, SERVER)
        assert "timed out" in msg.lower()
        assert hint is not None and SERVER in hint

    def test_read_timeout(self):
        exc = httpx.ReadTimeout("read timed out")
        msg, hint = resolve_error(exc, SERVER)
        assert "timed out" in msg.lower()
        assert hint is not None and SERVER in hint

    def test_connection_refused(self):
        exc = httpx.ConnectError("[Errno 111] Connection refused")
        msg, hint = resolve_error(exc, SERVER)
        assert "Connection refused" in msg
        assert hint is not None and SERVER in hint

    def test_connection_refused_windows(self):
        exc = httpx.ConnectError("[Errno 10061] actively refused it")
        msg, hint = resolve_error(exc, SERVER)
        assert "Connection refused" in msg
        assert hint is not None and SERVER in hint

    def test_dns_failure(self):
        exc = httpx.ConnectError("[Errno -2] Name or service not known")
        msg, hint = resolve_error(exc, SERVER)
        assert "resolve" in msg.lower()
        assert hint is not None and SERVER in hint

    def test_dns_failure_windows(self):
        exc = httpx.ConnectError("[Errno 11001] No such host is known")
        msg, hint = resolve_error(exc, SERVER)
        assert "resolve" in msg.lower()
        assert hint is not None and SERVER in hint

    def test_protocol_error(self):
        exc = httpx.ProtocolError("invalid protocol response")
        msg, hint = resolve_error(exc, SERVER)
        assert "protocol" in msg.lower()
        assert hint is not None and SERVER in hint

    def test_invalid_url(self):
        exc = httpx.InvalidURL("invalid url")
        msg, hint = resolve_error(exc, SERVER)
        assert "invalid" in msg.lower()
        assert hint is not None

    def test_unrecognised_error_returns_no_hint(self):
        exc = httpx.HTTPError("something unexpected")
        msg, hint = resolve_error(exc, SERVER)
        assert "Failed to contact server" in msg
        assert hint is None
