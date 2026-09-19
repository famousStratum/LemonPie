import os, httpx, json

from lemonpie.paths import CONFIG_FILE

def save_config(cfg):
    tmp = CONFIG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CONFIG_FILE)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        # default structure uses list-of-objects for models
        default_cfg = {"server": "http://127.0.0.1:11434", "default": None, "models": []}
        save_config(default_cfg)
        return default_cfg

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Ensure structure keys exist
    cfg.setdefault("server", None)
    cfg.setdefault("default", None)
    cfg.setdefault("models", [])
    return cfg

def resolve_server_host(cfg):
    return os.environ.get("OLLAMA_HOST") or cfg.get("server")

def is_valid_url(url):
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and p.netloc != ""
    except Exception:
        return False

def ensure_models_list(cfg):
    if not isinstance(cfg.get("models"), list):
        cfg["models"] = []

def build_timeout():
    return httpx.Timeout(connect=5.0, read=600.0, write=30.0, pool=5.0)
