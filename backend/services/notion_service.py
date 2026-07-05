"""
Notion Import — pulls pages/database rows from Notion and turns them into tasks.

Setup (free, ~3 min):
  1. https://www.notion.so/my-integrations -> "New integration"
  2. Copy the "Internal Integration Secret"
  3. In Notion, open the page/database to import from -> "..." -> "Connections"
     -> add your integration (required, otherwise the API can't see it)
  4. Put in backend/.env:
       NOTION_API_KEY=
       NOTION_DATABASE_ID=   (the database you want to import tasks from)
"""
import os
import requests

API_KEY = os.environ.get("NOTION_API_KEY", "")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
NOTION_VERSION = "2022-06-28"


def is_configured() -> bool:
    return bool(API_KEY and DATABASE_ID)


def _headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def fetch_database_rows() -> list:
    """
    Returns rows from the configured Notion database as simple task-like dicts.
    Assumes a "Name" title property; adjust property names to match your database.
    """
    if not is_configured():
        return []

    resp = requests.post(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])

    tasks = []
    for row in results:
        props = row.get("properties", {})
        title_prop = props.get("Name", {}).get("title", [])
        title = title_prop[0]["plain_text"] if title_prop else "(untitled)"
        tasks.append({"notion_id": row["id"], "title": title})

    return tasks
