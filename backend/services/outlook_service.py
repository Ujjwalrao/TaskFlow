"""
Outlook Calendar Integration — OAuth2 via Microsoft Graph API.

Setup (free, ~10 min):
  1. https://portal.azure.com -> "App registrations" -> "New registration"
  2. Redirect URI: http://localhost:5000/api/integrations/outlook/callback
  3. "Certificates & secrets" -> "New client secret"
  4. "API permissions" -> Add -> Microsoft Graph -> Calendars.ReadWrite
  5. Put these in backend/.env:
       OUTLOOK_CLIENT_ID=
       OUTLOOK_CLIENT_SECRET=
       OUTLOOK_TENANT_ID=common
"""
import os
import json
import requests
from database.db import get_db

CLIENT_ID = os.environ.get("OUTLOOK_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("OUTLOOK_CLIENT_SECRET", "")
TENANT_ID = os.environ.get("OUTLOOK_TENANT_ID", "common")
REDIRECT_URI = os.environ.get("OUTLOOK_REDIRECT_URI", "http://localhost:5000/api/integrations/outlook/callback")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = "Calendars.ReadWrite offline_access"


def is_configured() -> bool:
    return bool(CLIENT_ID and CLIENT_SECRET)


def get_auth_url() -> str:
    return (
        f"{AUTHORITY}/oauth2/v2.0/authorize"
        f"?client_id={CLIENT_ID}&response_type=code"
        f"&redirect_uri={REDIRECT_URI}&scope={SCOPES}"
    )


def exchange_code_for_token(code: str) -> dict:
    resp = requests.post(
        f"{AUTHORITY}/oauth2/v2.0/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
            "scope": SCOPES,
        },
        timeout=10,
    )
    resp.raise_for_status()
    token_data = resp.json()

    conn = get_db()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES ('outlook_token', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (json.dumps(token_data),),
    )
    conn.commit()
    conn.close()
    return token_data


def _get_access_token():
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key='outlook_token'").fetchone()
    conn.close()
    if not row:
        return None
    return json.loads(row["value"]).get("access_token")


def is_connected() -> bool:
    return _get_access_token() is not None


def push_task_to_calendar(task: dict) -> dict:
    token = _get_access_token()
    if not token or not task.get("due_date"):
        return {"synced": False, "reason": "not connected or no due date"}

    event = {
        "subject": task["title"],
        "body": {"contentType": "Text", "content": task.get("description") or "Created by TaskFlow"},
        "start": {"dateTime": f"{task['due_date']}T09:00:00", "timeZone": "UTC"},
        "end": {"dateTime": f"{task['due_date']}T10:00:00", "timeZone": "UTC"},
    }
    resp = requests.post(
        "https://graph.microsoft.com/v1.0/me/events",
        headers={"Authorization": f"Bearer {token}"},
        json=event,
        timeout=10,
    )
    if resp.ok:
        return {"synced": True, "event_id": resp.json().get("id")}
    return {"synced": False, "reason": resp.text}
