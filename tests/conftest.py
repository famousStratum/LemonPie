"""
Shared pytest fixtures for LemonPie's test suite.

The tricky part here is that `lemonpie.paths` computes CONFIG_FILE / SESSIONS_DIR /
CURRENT_FILE exactly once, at import time, from $LEMONPIE_CONFIG_DIR and
$LEMONPIE_SESSIONS_DIR. By the time any test runs, that module has already been
imported and those names are already bound to real strings. Setting the env vars
inside a fixture has no effect on values that were already computed.

Worse, `lemonpie.config` and `lemonpie.sessions.storage` each did
`from lemonpie.paths import CONFIG_FILE` / `from lemonpie.paths import CURRENT_FILE, SESSIONS_DIR`
— a value copy into their own module namespace, not a live reference back to
`lemonpie.paths`. So patching `lemonpie.paths.CONFIG_FILE` alone would not affect
`lemonpie.config.CONFIG_FILE`.

The `isolated_dirs` fixture below patches every one of those copies directly with
monkeypatch (which auto-reverts after each test), so each test gets its own throwaway
config file and sessions directory with no risk of touching the developer's real
~/.config/lemonpie or ~/.local/share/lemonpie.
"""

import json

import pytest

import lemonpie.config as config
import lemonpie.paths as paths
import lemonpie.sessions.storage as storage


@pytest.fixture
def isolated_dirs(tmp_path, monkeypatch):
    """Redirect all on-disk LemonPie state into a temp directory for one test."""
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    sessions_dir = data_dir / "sessions"
    config_dir.mkdir()
    sessions_dir.mkdir(parents=True)

    config_file = config_dir / "config.json"
    current_file = sessions_dir / ".current"

    # Keep the env vars themselves in sync too, for any code path that reads
    # them directly (e.g. a future subprocess-based test).
    monkeypatch.setenv("LEMONPIE_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("LEMONPIE_SESSIONS_DIR", str(sessions_dir))

    # lemonpie.paths itself
    monkeypatch.setattr(paths, "CONFIG_DIR", str(config_dir))
    monkeypatch.setattr(paths, "CONFIG_FILE", str(config_file))
    monkeypatch.setattr(paths, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(paths, "SESSIONS_DIR", str(sessions_dir))
    monkeypatch.setattr(paths, "CURRENT_FILE", str(current_file))

    # Every module that imported these names directly (own copies, not live refs)
    monkeypatch.setattr(config, "CONFIG_FILE", str(config_file))
    monkeypatch.setattr(storage, "SESSIONS_DIR", str(sessions_dir))
    monkeypatch.setattr(storage, "CURRENT_FILE", str(current_file))

    return {
        "config_dir": config_dir,
        "sessions_dir": sessions_dir,
        "config_file": config_file,
        "current_file": current_file,
    }


@pytest.fixture
def sample_cfg():
    """A minimal, valid config dict: one aliased model, set as default."""
    return {
        "server": "http://127.0.0.1:11434",
        "default": "qwen2.5-coder:3b",
        "models": [
            {"alias": "qwen", "name": "qwen2.5-coder:3b"},
        ],
    }


@pytest.fixture
def write_cfg(isolated_dirs, sample_cfg):
    """Write sample_cfg to the isolated config file and hand back the dict."""
    isolated_dirs["config_file"].write_text(json.dumps(sample_cfg), encoding="utf-8")
    return sample_cfg
