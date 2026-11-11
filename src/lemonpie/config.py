import json
import os
from urllib.parse import urlparse

import httpx

from lemonpie.paths import CONFIG_FILE


def save_config(cfg):
    tmp = CONFIG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CONFIG_FILE)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        # default structure uses list-of-objects for models
        default_cfg = {
            "backend": None,
            "server": None,
            "api_key": None,
            "default": None,
            "models": [],
        }
        save_config(default_cfg)
        return default_cfg

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Ensure structure keys exist
    cfg.setdefault("backend", None)
    cfg.setdefault("server", None)
    cfg.setdefault("api_key", None)
    cfg.setdefault("default", None)
    cfg.setdefault("models", [])
    return cfg


def resolve_server_host(cfg):
    return os.environ.get("LEMONPIE_HOST") or cfg.get("server")


def is_valid_url(url):
    try:
        p = urlparse(url)
    except (TypeError, AttributeError, ValueError):
        return False

    return p.scheme in ("http", "https") and bool(p.netloc)


def ensure_models_list(cfg):
    if not isinstance(cfg.get("models"), list):
        cfg["models"] = []


def config_file_path():
    """Return the active config file path.

    Accessing CONFIG_FILE through this function (rather than importing it
    directly) lets callers stay in sync with monkeypatching done by the test
    fixtures — they patch ``lemonpie.config.CONFIG_FILE``, so any code that
    reads it at call-time sees the patched value automatically.
    """
    return CONFIG_FILE


def build_timeout():
    return httpx.Timeout(connect=5.0, read=600.0, write=30.0, pool=5.0)
