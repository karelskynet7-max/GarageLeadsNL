from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters.manual import ManualAdapter
from .adapters.reddit import RedditAdapter
from .adapters.rss import RSSAdapter
from .config import load_config, load_env_file
from .filters import DUTCH_INCLUDE_KEYWORDS, DUTCH_NEGATIVE_KEYWORDS
from .pipeline import LeadPipeline
from .storage import Storage


def build_storage(data_dir: str | Path) -> Storage:
    base = Path(data_dir)
    base.mkdir(parents=True, exist_ok=True)
    return Storage(base / "leads.db")


def run_once(config: dict) -> list[str]:
    env = config.get("env", {})
    data_dir = env.get("DATA_DIR", "./data")
    storage = build_storage(data_dir)
    pipeline = LeadPipeline(
        storage=storage,
        keywords=config.get("keywords", DUTCH_INCLUDE_KEYWORDS),
        negative_keywords=config.get("negative_keywords", DUTCH_NEGATIVE_KEYWORDS),
        cities=config.get("cities", []),
        threshold=int(config.get("score_threshold", 50)),
    )

    found_urls: list[str] = []

    for adapter_name in ("reddit", "rss"):
        if not config.get("sources", {}).get(adapter_name, True):
            continue

        if adapter_name == "reddit":
            reddit = RedditAdapter(
                client_id=env.get("REDDIT_CLIENT_ID"),
                client_secret=env.get("REDDIT_CLIENT_SECRET"),
            )
            for lead in reddit.fetch():
                processed = pipeline.process(lead)
                if processed:
                    found_urls.append(processed.url)
                    print(f"[reddit] {processed.title} ({processed.score}) -> {processed.url}")
        elif adapter_name == "rss":
            rss = RSSAdapter()
            for lead in rss.fetch(config.get("rss_feeds", [])):
                processed = pipeline.process(lead)
                if processed:
                    found_urls.append(processed.url)
                    print(f"[rss] {processed.title} ({processed.score}) -> {processed.url}")

    if config.get("telegram_enabled", False):
        token = env.get("TELEGRAM_BOT_TOKEN")
        chat_id = env.get("TELEGRAM_CHAT_ID")
        if token and chat_id:
            from .notifier import TelegramNotifier

            notifier = TelegramNotifier(token, str(chat_id), storage)
            for lead in storage.list_leads(limit=10):
                notifier.send(
                    lead["title"],
                    int(lead["score"]),
                    json.loads(lead["matched_keywords"] or "[]"),
                    lead["location_hint"],
                    lead["url"],
                )

    if not found_urls:
        print("[dry-run] no leads above threshold")

    return found_urls


def command_run(args: argparse.Namespace) -> int:
    load_env_file()
    config = load_config()

    if args.once:
        run_once(config)
        print("Single run complete.")
        return 0

    print("Starting continuous monitoring (Ctrl+C to stop)...")
    import time

    interval_seconds = int(config.get("check_interval_minutes", 10)) * 60
    while True:
        run_once(config)
        time.sleep(interval_seconds)


def command_list(args: argparse.Namespace) -> int:
    load_env_file()
    config = load_config()
    storage = build_storage(config.get("env", {}).get("DATA_DIR", "./data"))
    for row in storage.list_leads(limit=20):
        print(f"{row['title']} | score={row['score']} | source={row['source']} | url={row['url']}")
    return 0


def command_purge(args: argparse.Namespace) -> int:
    load_env_file()
    config = load_config()
    storage = build_storage(config.get("env", {}).get("DATA_DIR", "./data"))
    deleted = storage.purge_retention(int(config.get("retention_days", 30)))
    print(f"Purged {deleted} lead records.")
    return 0


def command_add(args: argparse.Namespace) -> int:
    load_env_file()
    config = load_config()
    storage = build_storage(config.get("env", {}).get("DATA_DIR", "./data"))
    pipeline = LeadPipeline(
        storage=storage,
        keywords=config.get("keywords", DUTCH_INCLUDE_KEYWORDS),
        negative_keywords=config.get("negative_keywords", DUTCH_NEGATIVE_KEYWORDS),
        cities=config.get("cities", []),
        threshold=int(config.get("score_threshold", 50)),
    )

    lead = ManualAdapter().from_url(args.url, title=args.title, text=args.text)
    processed = pipeline.process(lead)
    if processed:
        print(f"Added lead: {processed.title} (score={processed.score})")
    else:
        print("Lead did not meet threshold.")
    return 0


def command_show_config(args: argparse.Namespace) -> int:
    load_env_file()
    print(load_config())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GarageLeadsNL")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the monitor")
    run_parser.add_argument("--once", action="store_true", help="Run once without continuous loop")
    run_parser.set_defaults(handler=command_run)

    leads_parser = subparsers.add_parser("leads", help="Lead management")
    leads_sub = leads_parser.add_subparsers(dest="leads_command", required=True)

    list_parser = leads_sub.add_parser("list", help="List stored leads")
    list_parser.set_defaults(handler=command_list)

    purge_parser = leads_sub.add_parser("purge", help="Purge old leads")
    purge_parser.set_defaults(handler=command_purge)

    add_parser = leads_sub.add_parser("add", help="Add a manual lead")
    add_parser.add_argument("url")
    add_parser.add_argument("--title", default="Manual lead")
    add_parser.add_argument("--text", default="")
    add_parser.set_defaults(handler=command_add)

    config_parser = subparsers.add_parser("config", help="Configuration")
    config_sub = config_parser.add_subparsers(dest="config_command", required=True)
    show_config_parser = config_sub.add_parser("show", help="Show configuration")
    show_config_parser.set_defaults(handler=command_show_config)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        raise SystemExit(1)
    raise SystemExit(handler(args))


if __name__ == "__main__":
    main()
