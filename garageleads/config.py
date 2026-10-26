from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

DEFAULT_CONFIG_PATH = Path("config.yaml")
DEFAULT_ENV_PATH = Path(".env")


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def load_env_file(path: str | Path = DEFAULT_ENV_PATH) -> None:
    load_dotenv(path, override=False)


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}

    env = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
        "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET"),
        "DATA_DIR": os.getenv("DATA_DIR"),
    }
    config["env"] = {key: value for key, value in env.items() if value is not None}
    config["telegram_enabled"] = _coerce_bool(config.get("telegram_enabled", False))
    config["sources"] = config.get("sources", {})
    config["sources"]["reddit"] = _coerce_bool(config["sources"].get("reddit", True))
    config["sources"]["rss"] = _coerce_bool(config["sources"].get("rss", True))
    config["sources"]["manual"] = _coerce_bool(config["sources"].get("manual", True))
    config["sources"]["b2b"] = _coerce_bool(config["sources"].get("b2b", False))
    return config
