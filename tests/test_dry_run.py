"""Integration tests for `lm --dry-run` behaviour in lemonpie.main."""

import json
from unittest.mock import MagicMock, patch

import pytest

from lemonpie.main import main


@pytest.fixture(autouse=True)
def mock_argv():
    with patch("sys.argv", ["lm", "--dry-run"]):
        yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_args(**overrides):
    """Build a parser-args mock with sensible defaults."""
    defaults = {
        "model": None,
        "new": False,
        "session": None,
        "list": False,
        "delete": None,
        "title": None,
        "close": False,
        "print": False,
        "delete_all": False,
        "dry_run": False,
        "prompt": [],
    }
    defaults.update(overrides)
    return MagicMock(**defaults)


# ---------------------------------------------------------------------------
# --dry-run: no prompt, no session
# ---------------------------------------------------------------------------

class TestDryRunNoPrompt:
    def test_exits_zero_and_prints_message(self, isolated_dirs, write_cfg, capsys):
        """No prompt + no current session → 'No messages to send', exit 0."""
        with patch("lemonpie.main.build_parser") as mock_parser_cls:
            mock_parser_cls.return_value.parse_args.return_value = _mock_args(dry_run=True)
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 0
        assert "No messages to send" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# --dry-run: prompt with no existing session
# ---------------------------------------------------------------------------

class TestDryRunPromptNoSession:
    def test_payload_contains_only_user_message(self, isolated_dirs, write_cfg, capsys):
        """Prompt + no session → payload has just the user message, no writes."""
        with patch("lemonpie.main.build_parser") as mock_parser_cls:
            mock_parser_cls.return_value.parse_args.return_value = _mock_args(
                dry_run=True, prompt=["hello world"]
            )
            with pytest.raises(SystemExit) as exc:
                main()

        assert exc.value.code == 0
        output = capsys.readouterr().out

        # Should start with the header line
        assert "=== Dry Run: HTTP Payload ===" in output

        # Parse the JSON and verify its contents
        # Output has header line, then JSON object on following lines
        json_part = output.split("=== Dry Run: HTTP Payload ===", 1)[1].strip()
        payload = json.loads(json_part)

        assert payload["model"] == "qwen2.5-coder:3b"
        assert payload["stream"] is True
        assert len(payload["messages"]) == 1
        assert payload["messages"][0] == {"role": "user", "content": "hello world"}

        # No session file should have been created
        session_files = list(isolated_dirs["session_dir"].glob("*.json"))
        assert len(session_files) == 0, (
            "dry-run with no session must not create session files"
        )


# ---------------------------------------------------------------------------
# --dry-run: -s flag takes precedence over current session pointer
# ---------------------------------------------------------------------------

class TestDryRunWithSessionFlag:
    def test_loads_specified_session_not_current(self, isolated_dirs, write_cfg, capsys):
        """-s <id> loads that session's history, not the current session's."""
        # Create two sessions with different history
        session_a = {
            "id": "20260101-000000-aaa",
            "model": "qwen2.5-coder:3b",
            "title": "Current Session",
            "history": [
                {"role": "user", "content": "current-only"},
                {"role": "assistant", "content": "from-current"},
            ],
        }
        session_b = {
            "id": "20260101-000000-bbb",
            "model": "qwen2.5-coder:3b",
            "title": "Target Session",
            "history": [
                {"role": "user", "content": "target-only"},
                {"role": "assistant", "content": "from-target"},
            ],
        }

        # Write session A as the "current" session
        isolated_dirs["current_file"].write_text("20260101-000000-aaa", encoding="utf-8")
        isolated_dirs["session_dir"].joinpath(
            "20260101-000000-aaa.json"
        ).write_text(json.dumps(session_a), encoding="utf-8")

        # Write session B (the one we want to load via -s)
        isolated_dirs["session_dir"].joinpath(
            "20260101-000000-bbb.json"
        ).write_text(json.dumps(session_b), encoding="utf-8")

        with patch("lemonpie.main.build_parser") as mock_parser_cls:
            mock_parser_cls.return_value.parse_args.return_value = _mock_args(
                dry_run=True,
                prompt=["added-later"],
                session="20260101-000000-bbb",
            )
            with pytest.raises(SystemExit) as exc:
                main()

        assert exc.value.code == 0
        output = capsys.readouterr().out

        json_part = output.split("=== Dry Run: HTTP Payload ===", 1)[1].strip()
        payload = json.loads(json_part)

        messages = [m["content"] for m in payload["messages"]]
        # Should contain target session history + prompt
        assert "target-only" in messages
        assert "from-target" in messages
        assert "added-later" in messages
        # Must NOT contain current session messages
        assert "current-only" not in messages
        assert "from-current" not in messages


# ---------------------------------------------------------------------------
# Regression guard: normal prompt flow still works
# ---------------------------------------------------------------------------

class TestNormalPromptFlow:
    def test_sends_request_via_stream_chat(self, isolated_dirs, write_cfg):
        """A normal prompt (no --dry-run) reaches stream_chat without crashing."""
        with patch("lemonpie.main.build_parser") as mock_parser_cls:
            mock_parser_cls.return_value.parse_args.return_value = _mock_args(
                prompt=["test prompt"]
            )
            with patch("lemonpie.main.StatusSpinner") as mock_spinner_cls:
                mock_spinner_cls.return_value = MagicMock()
                with patch("lemonpie.main.stream_chat") as mock_stream:
                    mock_stream.return_value = iter(["got response"])
                    # No exception should be raised
                    main()

        # Verify that stream_chat was called
        assert mock_stream.called

        # Verify it received a properly-structured payload
        _, payload = mock_stream.call_args.args
        assert isinstance(payload, dict)
        assert "messages" in payload
        assert payload["stream"] is True

        # The user message should be in the payload
        messages = payload["messages"]
        user_contents = [m["content"] for m in messages if m["role"] == "user"]
        assert "test prompt" in user_contents


# ---------------------------------------------------------------------------
# --dry-run intercepts for write/delete operations
# ---------------------------------------------------------------------------

class TestDryRunIntercepts:
    def test_delete_prints_message_and_exits_zero(self, write_cfg, capsys):
        with patch("lemonpie.main.build_parser") as mock_parser_cls:
            mock_parser_cls.return_value.parse_args.return_value = _mock_args(
                dry_run=True, delete="abc123"
            )
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 0
        assert "Would delete session abc123." in capsys.readouterr().out

    def test_delete_all_prints_message_and_exits_zero(self, write_cfg, capsys):
        with patch("lemonpie.main.build_parser") as mock_parser_cls:
            mock_parser_cls.return_value.parse_args.return_value = _mock_args(
                dry_run=True, delete_all=True
            )
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 0
        assert "Would delete all sessions." in capsys.readouterr().out

    def test_close_prints_message_and_exits_zero(self, write_cfg, capsys):
        with patch("lemonpie.main.build_parser") as mock_parser_cls:
            mock_parser_cls.return_value.parse_args.return_value = _mock_args(
                dry_run=True, close=True
            )
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 0
        assert "Would close the current session." in capsys.readouterr().out
