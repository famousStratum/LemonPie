"""Tests for session creation, retrieval, and saving logic in
lemonpie.sessions.storage. Every test uses the isolated_dirs fixture from
conftest.py so nothing here touches a real ~/.local/share/lemonpie/sessions.
"""

import json

import pytest

from lemonpie.sessions import storage


# ---------------------------------------------------------------------------
# create_session / default_title
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="create_session() calls now_ts() twice, so created_at and updated_at differ by microseconds instead of matching. Bug, not a test issue — fix by computing the timestamp once and reusing it for both fields.",
    strict=True,
)
def test_create_session_writes_file_and_sets_current(isolated_dirs):
    session = storage.create_session(["hello", "world"], "qwen2.5-coder:3b")

    assert session["model"] == "qwen2.5-coder:3b"
    assert session["title"] == "hello world"
    assert session["history"] == []
    assert session["created_at"] == session["updated_at"]

    saved_path = isolated_dirs["sessions_dir"] / f"{session['id']}.json"
    assert saved_path.exists()
    on_disk = json.loads(saved_path.read_text(encoding="utf-8"))
    assert on_disk["id"] == session["id"]

    assert storage.read_current() == session["id"]


def test_create_session_without_prompt_uses_placeholder_title(isolated_dirs):
    session = storage.create_session([], "qwen2.5-coder:3b")
    assert session["title"] == "<no title>"


def test_default_title_truncates_long_prompts(isolated_dirs):
    long_prompt = "x" * 80
    title = storage.default_title(long_prompt)
    assert len(title) <= storage.MAX_TITLE_LEN + 1  # +1 for the trailing "…"
    assert title.endswith("…")


def test_default_title_leaves_short_prompts_untouched(isolated_dirs):
    assert storage.default_title("short prompt") == "short prompt"


# ---------------------------------------------------------------------------
# save_session / load_session
# ---------------------------------------------------------------------------

def test_save_and_load_session_round_trip(isolated_dirs):
    session = storage.create_session(["ping"], "qwen")
    session["history"].append(
        {"role": "user", "content": "ping", "ts": "2026-09-22T00:00:00+00:00"}
    )
    storage.save_session(session["id"], session)

    loaded = storage.load_session(session["id"])
    assert loaded["history"] == session["history"]
    assert loaded["created_at"] == session["created_at"]


def test_load_session_missing_returns_empty_shell(isolated_dirs):
    loaded = storage.load_session("does-not-exist")
    assert loaded == {
        "id": "does-not-exist",
        "title": None,
        "history": [],
        "created_at": None,
        "updated_at": None,
    }


def test_load_session_backfills_missing_timestamps_from_history(isolated_dirs):
    # Simulate an older/hand-edited session file with no created_at/updated_at,
    # written directly rather than via create_session().
    session_id = "20260101-000000"
    raw = {
        "id": session_id,
        "model": "qwen",
        "title": "old session",
        "history": [
            {"role": "user", "content": "hi", "ts": "2026-01-01T00:00:00+00:00"},
            {"role": "assistant", "content": "hello", "ts": "2026-01-01T00:00:05+00:00"},
        ],
    }
    (isolated_dirs["sessions_dir"] / f"{session_id}.json").write_text(
        json.dumps(raw), encoding="utf-8"
    )

    loaded = storage.load_session(session_id)
    assert loaded["created_at"] == "2026-01-01T00:00:00+00:00"
    assert loaded["updated_at"] == "2026-01-01T00:00:05+00:00"


def test_load_session_backfills_from_mtime_when_history_empty(isolated_dirs):
    session_id = "20260101-000001"
    raw = {"id": session_id, "model": "qwen", "title": "empty", "history": []}
    (isolated_dirs["sessions_dir"] / f"{session_id}.json").write_text(
        json.dumps(raw), encoding="utf-8"
    )

    loaded = storage.load_session(session_id)
    assert loaded["created_at"] is not None
    assert loaded["updated_at"] == loaded["created_at"]


# ---------------------------------------------------------------------------
# delete_session / delete_all_sessions
# ---------------------------------------------------------------------------

def test_delete_session_removes_file_and_reports_result(isolated_dirs):
    session = storage.create_session(["bye"], "qwen")
    assert storage.delete_session(session["id"]) is True
    assert not (isolated_dirs["sessions_dir"] / f"{session['id']}.json").exists()
    assert storage.delete_session(session["id"]) is False  # already gone


@pytest.mark.xfail(
    reason="create_session() derives session IDs from datetime.now().strftime('%Y%m%d-%H%M%S'), 1-second resolution. Two sessions created within the same second collide and the second silently overwrites the first's file. Bug, not a test issue — fix by adding sub-second precision (or a uuid suffix) to the session ID.",
    strict=True,
)
def test_delete_all_sessions_clears_dir_and_current(isolated_dirs):
    storage.create_session(["one"], "qwen")
    storage.create_session(["two"], "qwen")
    assert storage.read_current() is not None

    count = storage.delete_all_sessions()

    assert count == 2
    assert storage.read_current() is None
    assert list(isolated_dirs["sessions_dir"].glob("*.json")) == []


# ---------------------------------------------------------------------------
# list_sessions
# ---------------------------------------------------------------------------

def test_list_sessions_marks_current_and_ignores_non_json(isolated_dirs):
    s1 = storage.create_session(["first"], "qwen")
    s2 = storage.create_session(["second"], "qwen")  # becomes current
    (isolated_dirs["sessions_dir"] / "notes.txt").write_text("ignore me", encoding="utf-8")

    sessions = storage.list_sessions()
    ids = {row[0] for row in sessions}
    assert ids == {s1["id"], s2["id"]}

    current_rows = [row for row in sessions if row[4] == "*"]
    assert len(current_rows) == 1
    assert current_rows[0][0] == s2["id"]


def test_list_sessions_skips_invalid_json_without_crashing(isolated_dirs):
    storage.create_session(["ok"], "qwen")
    (isolated_dirs["sessions_dir"] / "corrupt.json").write_text(
        "{not valid json", encoding="utf-8"
    )

    sessions = storage.list_sessions()
    assert len(sessions) == 1


# ---------------------------------------------------------------------------
# current-session pointer
# ---------------------------------------------------------------------------

def test_write_read_clear_current(isolated_dirs):
    assert storage.read_current() is None
    storage.write_current("abc")
    assert storage.read_current() == "abc"
    storage.clear_current()
    assert storage.read_current() is None


def test_close_session_clears_current(isolated_dirs):
    storage.write_current("abc")
    storage.close_session()
    assert storage.read_current() is None


# ---------------------------------------------------------------------------
# set_title
# ---------------------------------------------------------------------------

def test_set_title_rejects_overlong_title(isolated_dirs):
    session = storage.create_session(["hi"], "qwen")
    too_long = "x" * (storage.MAX_TITLE_LEN + 1)
    assert storage.set_title(session, too_long) is False
    reloaded = storage.load_session(session["id"])
    assert reloaded["title"] != too_long


def test_set_title_updates_and_persists(isolated_dirs):
    session = storage.create_session(["hi"], "qwen")
    assert storage.set_title(session, "New title") is True
    reloaded = storage.load_session(session["id"])
    assert reloaded["title"] == "New title"


# ---------------------------------------------------------------------------
# resolve_session
# ---------------------------------------------------------------------------

class DummyArgs:
    """Minimal stand-in for the argparse.Namespace fields resolve_session reads."""

    def __init__(self, new=False, session=None, prompt=None):
        self.new = new
        self.session = session
        self.prompt = prompt or []


def test_resolve_session_new_flag_creates_session(isolated_dirs):
    args = DummyArgs(new=True, prompt=["fresh", "start"])
    session = storage.resolve_session(args, "qwen", current_id=None)
    assert session["title"] == "fresh start"


def test_resolve_session_with_explicit_session_id_applies_model_and_sets_current(isolated_dirs):
    existing = storage.create_session(["first"], "qwen")
    storage.clear_current()

    args = DummyArgs(session=existing["id"])
    session = storage.resolve_session(args, "qwen2.5-coder:1.5b", current_id=None)

    assert session["id"] == existing["id"]
    assert session["model"] == "qwen2.5-coder:1.5b"
    assert storage.read_current() == existing["id"]


def test_resolve_session_falls_back_to_current_id(isolated_dirs):
    existing = storage.create_session(["first"], "qwen")
    args = DummyArgs()
    session = storage.resolve_session(args, "qwen", current_id=existing["id"])
    assert session["id"] == existing["id"]


def test_resolve_session_creates_when_nothing_else_applies(isolated_dirs):
    args = DummyArgs(prompt=["brand", "new"])
    session = storage.resolve_session(args, "qwen", current_id=None)
    assert session["title"] == "brand new"


# ---------------------------------------------------------------------------
# functions that call input() / sys.exit()
# ---------------------------------------------------------------------------

def test_delete_session_by_id_confirmed_removes_file(isolated_dirs, monkeypatch):
    session = storage.create_session(["gone soon"], "qwen")
    monkeypatch.setattr("builtins.input", lambda _: "y")
    storage.delete_session_by_id(session["id"])
    assert not (isolated_dirs["sessions_dir"] / f"{session['id']}.json").exists()


def test_delete_session_by_id_aborted_keeps_file(isolated_dirs, monkeypatch):
    session = storage.create_session(["stay"], "qwen")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    storage.delete_session_by_id(session["id"])
    assert (isolated_dirs["sessions_dir"] / f"{session['id']}.json").exists()


def test_update_title_on_existing_session_without_prompt_exits_zero(isolated_dirs):
    session = storage.create_session(["hi"], "qwen")
    with pytest.raises(SystemExit) as exc_info:
        storage.update_title(session, "qwen", "New title", prompt=None)
    assert exc_info.value.code == 0
    assert storage.load_session(session["id"])["title"] == "New title"


def test_update_title_on_existing_session_with_prompt_returns_session(isolated_dirs):
    session = storage.create_session(["hi"], "qwen")
    result = storage.update_title(session, "qwen", "New title", prompt=["more"])
    assert result["title"] == "New title"


def test_update_title_with_no_session_confirmed_creates_one(isolated_dirs, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    with pytest.raises(SystemExit):
        storage.update_title(None, "qwen", "Brand new", prompt=None)
    sessions = storage.list_sessions()
    assert any(row[1] == "Brand new" for row in sessions)


def test_update_title_with_no_session_aborted_exits_zero(isolated_dirs, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    with pytest.raises(SystemExit) as exc_info:
        storage.update_title(None, "qwen", "Nope", prompt=None)
    assert exc_info.value.code == 0
