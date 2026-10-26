from __future__ import annotations

import json
from pathlib import Path

import yaml
from dotenv import load_dotenv


def load_env_file(path: str | Path = ".env") -> None:
    load_dotenv(path, override=False)


def load_config(path: str | Path = "config.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}

    config.setdefault("keywords", [])
    config.setdefault("negative_keywords", [])
    config.setdefault("cities", [])
    config.setdefault("sources", {})
    config["sources"].setdefault("reddit", True)
    config["sources"].setdefault("rss", True)
    config["sources"].setdefault("manual", True)
    config["sources"].setdefault("b2b", False)
    config.setdefault("telegram_enabled", False)
    config.setdefault("retention_days", 30)
    config.setdefault("score_threshold", 50)
    config.setdefault("check_interval_minutes", 10)
    config.setdefault("rss_feeds", [])
    return config
