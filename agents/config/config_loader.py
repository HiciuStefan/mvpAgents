import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).resolve().parent / "user_config.json"

def load_user_profile() -> Dict[str, Any]:
    """Load the user JSON profile from agents/config/user_config.json."""
    with open(CONFIG_PATH, encoding="utf-8") as fp:
        return json.load(fp)
