import os

# Inner package directory: ~/lemonpie/lemonpie
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# Project root directory: ~/lemonpie
PROJECT_ROOT = os.path.abspath(os.path.join(PACKAGE_DIR, ".."))

# Config file in project root
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")

# Sessions directory: precedence given to $LEMONPIE_SESSIONS_DIR environment variable,
# falling back to root/sessions
SESSIONS_DIR = os.environ.get(
    "LEMONPIE_SESSIONS_DIR", 
    os.path.join(PROJECT_ROOT, "sessions")
)
os.makedirs(SESSIONS_DIR, exist_ok=True)

CURRENT_FILE = os.path.join(SESSIONS_DIR, ".current")
