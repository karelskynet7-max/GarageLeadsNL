# GarageLeadsNL

GarageLeadsNL is a legal, GDPR-aware monitoring system for Dutch car repair businesses. It watches public sources for repair-intent signals, scores them, and alerts the business owner through Telegram. It never sends direct messages or auto-outreach to consumers.

The project is designed for:
- public signal monitoring only
- Dutch-language lead signals
- Telegram owner alerts
- GDPR-minimal data retention
- optional, off-by-default B2B outreach controls

## Legal notice
This project is intentionally constrained to public, lawful sources and never:
- scrapes login-gated content
- bypasses anti-bot protections
- stores personal contact details such as names, emails, or phone numbers
- auto-DMs, auto-comments, or auto-emails consumers

The system stores only necessary items:
- post text
- URL
- timestamp
- derived score

## GDPR and retention
The default retention window is 30 days. Old records can be purged via:

```bash
python -m garageleads leads purge
```

## Features
- Reddit source adapter
- RSS/Google News adapter
- Manual lead import via URL or text
- Deduplication based on normalized source+title+URL
- Dutch keyword filtering and urgency scoring
- Geo boost for Dutch cities and regions
- SQLite storage using WAL mode
- Telegram alerting with owner-only chat ID
- Docker deployment

## Tech stack
- Python 3.11+
- httpx
- feedparser
- pydantic
- SQLite3 standard library
- APScheduler
- python-dotenv
- Telegram Bot API over httpx
- Docker + docker-compose
- pytest

## Setup
1. Create a virtual environment.
2. Copy `.env.example` to `.env` and fill in your values.
3. Review `config.yaml`.
4. Install dependencies.
5. Run the monitor once:

```bash
python -m garageleads run --once
```

## Telegram setup with @BotFather
1. Open Telegram.
2. Message `@BotFather`.
3. Use `/newbot` to create your bot.
4. Copy the bot token.
5. Add the bot to your private garage-owner Telegram chat.
6. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.

## CLI
- `python -m garageleads run`
- `python -m garageleads run --once`
- `python -m garageleads leads list`
- `python -m garageleads leads purge`
- `python -m garageleads leads add https://example.com/post --title "Auto kapot" --text "...