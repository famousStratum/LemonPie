import os

from platformdirs import user_config_dir, user_data_dir

APP_NAME = "lemonpie"

# Config directory: OS-appropriate user config location
# (~/.config/lemonpie, %LOCALAPPDATA%\lemonpie, ~/Library/Application Support/lemonpie).
# Override with $LEMONPIE_CONFIG_DIR.
CONFIG_DIR = os.environ.get(
    "LEMONPIE_CONFIG_DIR", user_config_dir(APP_NAME, appauthor=False)
)
os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Sessions directory: OS-appropriate user data location.
DATA_DIR = user_data_dir(APP_NAME, appauthor=False)
SESSION_DIR = os.environ.get("LEMONPIE_SESSION_DIR", os.path.join(DATA_DIR, "sessions"))
os.makedirs(SESSION_DIR, exist_ok=True)

CURRENT_FILE = os.path.join(SESSION_DIR, ".current")
