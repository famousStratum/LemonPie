import os, httpx, json

from lemonpie.paths import CONFIG_FILE

def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

def resolve_server_host(cfg):
    return os.environ.get("OLLAMA_HOST") or cfg.get("server")

def build_timeout():
    return httpx.Timeout(connect=5.0, read=600.0, write=30.0, pool=5.0)
