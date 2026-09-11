"""
ExpedUP - Persistent Settings Manager
Handles loading, saving, validating, and resetting application settings via settings.json.
"""

import os
import json
from typing import Dict, Any, List

from config import SOCIAL_PLATFORMS, DOMAIN_TLDS, DEFAULT_EXPORT_DIR

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

TEXT_SCALE_MAP: Dict[str, float] = {
    "Normal (100%)": 1.0,
    "Large (110%)": 1.1,
    "Extra Large (120%)": 1.2
}

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "Light",
    "text_size": "Large (110%)",
    "default_depth": "Deep (Multi-Engine)",
    "export_dir": DEFAULT_EXPORT_DIR,
    "auto_export_all": False,
    "request_timeout": 12,
    "min_delay": 0.8,
    "max_delay": 1.4,
    "user_agent_rotation": True,
    "enabled_platforms": [p["name"] for p in SOCIAL_PLATFORMS],
    "domain_tlds": list(DOMAIN_TLDS)
}


def load_settings() -> Dict[str, Any]:
    """Load settings from disk, falling back to defaults for missing keys."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Merge with defaults to guarantee all expected keys exist
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except Exception as e:
        print(f"[WARN] Failed to load settings.json ({e}), reverting to defaults.")
        return dict(DEFAULT_SETTINGS)


def save_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and write settings to disk."""
    clean_data = dict(DEFAULT_SETTINGS)
    clean_data.update(data)

    if clean_data.get("text_size") not in TEXT_SCALE_MAP:
        clean_data["text_size"] = "Large (110%)"

    # Sanitize numeric bounds
    try:
        clean_data["request_timeout"] = max(3, min(60, int(clean_data.get("request_timeout", 12))))
        clean_data["min_delay"] = max(0.1, min(10.0, float(clean_data.get("min_delay", 0.8))))
        clean_data["max_delay"] = max(clean_data["min_delay"], min(15.0, float(clean_data.get("max_delay", 1.4))))
    except (ValueError, TypeError):
        clean_data["request_timeout"] = 12
        clean_data["min_delay"] = 0.8
        clean_data["max_delay"] = 1.4

    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to write settings.json: {e}")

    return clean_data


def reset_to_defaults() -> Dict[str, Any]:
    """Reset configuration back to factory settings."""
    return save_settings(DEFAULT_SETTINGS)


def get_setting(key: str, default: Any = None) -> Any:
    """Retrieve a single setting value."""
    settings = load_settings()
    return settings.get(key, default)
