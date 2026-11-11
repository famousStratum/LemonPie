"""Integration tests for lmConfig sub-commands.

Currently covers ``cmd_init`` — the interactive setup wizard introduced in
lmConfig --init.

Approach
--------
``cmd_init`` is interactive: it calls ``input()`` (directly and via
``confirm()`` which also calls ``input()``).  We mock ``builtins.input``
globally with an iterator so every prompt consumes the next queued response
in order, making the full interaction deterministic.

``fetch_available_models`` makes a network request, so every test that reaches
the server-verification step mocks it at the module level via monkeypatch.

All tests that touch the filesystem use the ``isolated_dirs`` fixture from
conftest.py, which redirects ``lemonpie.config.CONFIG_FILE`` and the session
paths to a throw-away temp directory.

Input sequence for cmd_init (new flow)
---------------------------------------
1. Backend selection          → digit ("1"=llama.cpp, "2"=Ollama, "3"=LM Studio, "4"=Other)
2. Local? confirm             → "y" / "n"
   2a. If local + known port  → digit ("1"=default URL, "2"=custom)
       2a-custom              → URL string
   2b. If not local           → URL string
3. [Server verification — mocked or skipped with --force]
4. Model selection / manual add prompts
5. Default model prompts
"""

import json

from lemonpie.cli.config_cmd import cmd_init

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_input(responses):
    """Return a lambda that pops from *responses* on each call."""
    it = iter(responses)
    return lambda _prompt="": next(it)


def _read_cfg(isolated_dirs):
    return json.loads(isolated_dirs["config_file"].read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# --force mode (skips server verification entirely)
# ---------------------------------------------------------------------------


class TestCmdInitForce:
    def test_force_fresh_no_models(self, isolated_dirs, monkeypatch):
        """--force, Ollama local default URL, skip manual model entry."""
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",  # Ollama
                "y",  # local
                "1",  # default URL
                "n",  # add model manually? no
            ]),
        )
        assert cmd_init(force=True) == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["backend"] == "ollama"
        assert cfg["server"] == "http://localhost:11434"
        assert cfg["models"] == []
        assert cfg["default"] is None

    def test_force_custom_server(self, isolated_dirs, monkeypatch):
        """--force, Ollama remote custom URL accepted without contacting it."""
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",                          # Ollama
                "n",                          # not local
                "http://192.168.1.10:11434",  # remote URL
                "n",                          # no models
            ]),
        )
        assert cmd_init(force=True) == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["backend"] == "ollama"
        assert cfg["server"] == "http://192.168.1.10:11434"

    def test_force_manual_model_with_alias_set_as_default(
        self, isolated_dirs, monkeypatch
    ):
        """--force, add one model manually with alias, set as default."""
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",               # Ollama
                "y",               # local
                "1",               # default URL
                "y",               # add model manually?
                "qwen2.5-coder:3b",  # model name
                "qwen",            # alias
                "n",               # add another?
                "y",               # set as default?
            ]),
        )
        assert cmd_init(force=True) == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == [{"alias": "qwen", "name": "qwen2.5-coder:3b"}]
        assert cfg["default"] == "qwen2.5-coder:3b"

    def test_force_manual_model_no_alias(self, isolated_dirs, monkeypatch):
        """--force, add one model with no alias; decline set-as-default."""
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",               # Ollama
                "y",               # local
                "1",               # default URL
                "y",               # add model manually?
                "qwen2.5-coder:3b",
                "",                # no alias
                "n",               # add another?
                "n",               # set as default?
            ]),
        )
        assert cmd_init(force=True) == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == [{"alias": None, "name": "qwen2.5-coder:3b"}]
        assert cfg["default"] is None

    def test_force_two_models_pick_second_as_default(self, isolated_dirs, monkeypatch):
        """--force, two models added; pick the second as default."""
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",               # Ollama
                "y",               # local
                "1",               # default URL
                "y",               # add model?
                "qwen2.5-coder:3b",
                "qwen",
                "y",               # add another?
                "llama3.2:1b",
                "llama",
                "n",               # no more
                "y",               # set default?
                "2",               # pick model 2
            ]),
        )
        assert cmd_init(force=True) == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["default"] == "llama3.2:1b"
        assert len(cfg["models"]) == 2


# ---------------------------------------------------------------------------
# Server reachable — model selection from server list
# ---------------------------------------------------------------------------


class TestCmdInitServerOk:
    def _mock_server(self, monkeypatch, models):
        """Patch fetch_available_models to return *models* with no error."""
        monkeypatch.setattr(
            "lemonpie.cli.config_cmd.fetch_available_models",
            lambda _server: (models, None),
        )

    def test_server_ok_select_one_model_with_alias(self, isolated_dirs, monkeypatch):
        """Server returns two models; user selects model 1 with alias."""
        self._mock_server(monkeypatch, ["qwen2.5-coder:3b", "llama3.2:1b"])
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",    # Ollama
                "y",    # local
                "1",    # default URL
                "1",    # select model 1
                "qwen", # alias
                "y",    # set as default?
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == [{"alias": "qwen", "name": "qwen2.5-coder:3b"}]
        assert cfg["default"] == "qwen2.5-coder:3b"

    def test_server_ok_select_multiple_models_pick_default(
        self, isolated_dirs, monkeypatch
    ):
        """User selects both server models; picks second as default."""
        self._mock_server(monkeypatch, ["qwen2.5-coder:3b", "llama3.2:1b"])
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",    # Ollama
                "y",    # local
                "1",    # default URL
                "1 2",  # select both
                "qwen", # alias for model 1
                "",     # no alias for model 2
                "y",    # set default?
                "2",    # pick model 2
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["default"] == "llama3.2:1b"
        assert len(cfg["models"]) == 2

    def test_server_ok_skip_selection(self, isolated_dirs, monkeypatch):
        """User presses Enter on the model-selection prompt — no models added."""
        self._mock_server(monkeypatch, ["qwen2.5-coder:3b"])
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",  # Ollama
                "y",  # local
                "1",  # default URL
                "",   # skip selection (Enter)
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == []
        assert cfg["default"] is None

    def test_server_ok_selection_invalid_tokens_ignored(
        self, isolated_dirs, monkeypatch
    ):
        """Out-of-range and non-numeric tokens are skipped gracefully."""
        self._mock_server(monkeypatch, ["qwen2.5-coder:3b"])
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",          # Ollama
                "y",          # local
                "1",          # default URL
                "0 99 abc 1", # 0 and 99 out of range, 'abc' invalid, 1 valid
                "qwen",       # alias for model 1
                "y",          # set as default
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == [{"alias": "qwen", "name": "qwen2.5-coder:3b"}]

    def test_server_ok_no_models_installed_skip_manual(
        self, isolated_dirs, monkeypatch
    ):
        """Server reachable but no models installed; user skips manual add."""
        self._mock_server(monkeypatch, [])
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",  # Ollama
                "y",  # local
                "1",  # default URL
                "n",  # skip manual add
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == []

    def test_server_ok_no_models_installed_manual_add(self, isolated_dirs, monkeypatch):
        """Server reachable, no models installed; user adds one manually."""
        self._mock_server(monkeypatch, [])
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",               # Ollama
                "y",               # local
                "1",               # default URL
                "y",               # add manually?
                "qwen2.5-coder:3b",
                "qwen",
                "n",               # add another?
                "y",               # set as default?
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == [{"alias": "qwen", "name": "qwen2.5-coder:3b"}]
        assert cfg["default"] == "qwen2.5-coder:3b"


# ---------------------------------------------------------------------------
# Server unreachable
# ---------------------------------------------------------------------------


class TestCmdInitServerUnreachable:
    def _mock_error(self, monkeypatch, err="Connection refused"):
        monkeypatch.setattr(
            "lemonpie.cli.config_cmd.fetch_available_models",
            lambda _server: ([], err),
        )

    def test_unreachable_user_aborts(self, isolated_dirs, monkeypatch):
        """Server unreachable; user declines to continue — returns 1."""
        self._mock_error(monkeypatch)
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",  # Ollama
                "y",  # local
                "1",  # default URL
                "n",  # abort after error
            ]),
        )
        assert cmd_init() == 1
        assert not isolated_dirs["config_file"].exists()

    def test_unreachable_continue_save_model(self, isolated_dirs, monkeypatch):
        """Server unreachable; user continues, adds model, config written."""
        self._mock_error(monkeypatch)
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",               # Ollama
                "y",               # local
                "1",               # default URL
                "y",               # continue without verification?
                "y",               # add manually?
                "qwen2.5-coder:3b",
                "qwen",
                "n",               # no more models
                "y",               # set as default?
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["server"] == "http://localhost:11434"
        assert cfg["models"] == [{"alias": "qwen", "name": "qwen2.5-coder:3b"}]
        assert cfg["default"] == "qwen2.5-coder:3b"

    def test_unreachable_continue_no_models(self, isolated_dirs, monkeypatch):
        """Server unreachable; user continues but declines to add models."""
        self._mock_error(monkeypatch)
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",  # Ollama
                "y",  # local
                "1",  # default URL
                "y",  # continue without verification?
                "n",  # no manual models
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == []


# ---------------------------------------------------------------------------
# Existing config
# ---------------------------------------------------------------------------


class TestCmdInitExistingConfig:
    def test_existing_config_user_aborts(self, write_cfg, isolated_dirs, monkeypatch):
        """Existing config: user declines reinit — returns 1, file unchanged."""
        monkeypatch.setattr("builtins.input", _make_input(["n"]))
        assert cmd_init(force=True) == 1

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"][0]["alias"] == "qwen"

    def test_existing_config_reinit(self, write_cfg, isolated_dirs, monkeypatch):
        """Existing config: user confirms — config is completely replaced."""
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "y",  # confirm reinit
                "2",  # Ollama
                "y",  # local
                "1",  # default URL
                "n",  # no models
            ]),
        )
        assert cmd_init(force=True) == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"] == []
        assert cfg["server"] == "http://localhost:11434"


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


class TestCmdInitInputValidation:
    def test_invalid_url_loops_until_valid(self, isolated_dirs, monkeypatch):
        """Bad URL triggers a re-prompt; second attempt accepted."""
        monkeypatch.setattr(
            "lemonpie.cli.config_cmd.fetch_available_models",
            lambda _: ([], None),
        )
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "4",                      # Other (no default port → custom URL)
                "y",                      # local
                "not-a-url",              # invalid
                "also bad",               # invalid
                "http://127.0.0.1:11434", # valid
                "n",                      # no models
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["server"] == "http://127.0.0.1:11434"

    def test_empty_model_name_loops_until_non_empty(self, isolated_dirs, monkeypatch):
        """Blank model name in manual-entry mode triggers a re-prompt."""
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",               # Ollama
                "y",               # local
                "1",               # default URL
                "y",               # add model manually?
                "",                # empty name — invalid
                "",                # still empty — still invalid
                "qwen2.5-coder:3b",
                "qwen",
                "n",               # no more
                "y",               # set as default
            ]),
        )
        assert cmd_init(force=True) == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["models"][0]["name"] == "qwen2.5-coder:3b"

    def test_invalid_default_number_loops_until_valid(self, isolated_dirs, monkeypatch):
        """Out-of-range and non-numeric entries in the default-pick loop are retried."""
        monkeypatch.setattr(
            "lemonpie.cli.config_cmd.fetch_available_models",
            lambda _: (["qwen2.5-coder:3b", "llama3.2:1b"], None),
        )
        monkeypatch.setattr(
            "builtins.input",
            _make_input([
                "2",    # Ollama
                "y",    # local
                "1",    # default URL
                "1 2",  # select both models
                "qwen", # alias for model 1
                "",     # no alias for model 2
                "y",    # set default?
                "5",    # out of range
                "abc",  # not a number
                "1",    # valid — pick first
            ]),
        )
        assert cmd_init() == 0

        cfg = _read_cfg(isolated_dirs)
        assert cfg["default"] == "qwen2.5-coder:3b"
