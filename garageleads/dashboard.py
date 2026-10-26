from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from .storage import Storage


def build_dashboard(storage: Storage) -> FastAPI:
    app = FastAPI(title="GarageLeadsNL Dashboard")

    @app.get("/")
    async def index():
        rows = storage.list_leads(limit=25)
        html = "<html><body><h1>GarageLeadsNL</h1><ul>"
        for row in rows:
            html += f"<li><strong>{row['title']}</strong> ({row['score']}) - <a href='{row['url']}'>{row['url']}</a></li>"
        html += "</ul></body></html>"
        return html

    return app
