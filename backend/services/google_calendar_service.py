"""
Google Calendar Integration — OAuth2 + two-way sync.

Requires a Google Cloud OAuth Client (Web application type) with:
    Authorized redirect URI: http://localhost:5000/api/integrations/google/callback
    (add your production backend URL too once deployed)

Credentials are read from environment variables — never hardcode them:
    GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET
    GOOGLE_REDIRECT_URI  (defaults to the localhost callback above)
"""
import os
import json
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from database.db import get_db

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:5000/api/integrations/google/callback")


def _client_config():
    return {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }


def is_configured() -> bool:
    return bool(CLIENT_ID and CLIENT_SECRET)


def get_auth_url() -> str:
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=REDIRECT_URI)
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    return auth_url


def exchange_code_for_token(code: str) -> dict:
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=REDIRECT_URI)
    flow.fetch_token(code=code)
    creds = flow.credentials
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
    conn = get_db()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES ('google_calendar_token', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (json.dumps(token_data),),
    )
    conn.commit()
    conn.close()
    return token_data


def _get_credentials():
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key='google_calendar_token'").fetchone()
    conn.close()
    if not row:
        return None
    data = json.loads(row["value"])
    return Credentials(
        token=data["token"],
        refresh_token=data["refresh_token"],
        token_uri=data["token_uri"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=data["scopes"],
    )


def is_connected() -> bool:
    return _get_credentials() is not None


def push_task_to_calendar(task: dict) -> dict:
    """Create/update a Google Calendar event for a task with a due date."""
    creds = _get_credentials()
    if not creds or not task.get("due_date"):
        return {"synced": False, "reason": "not connected or no due date"}

    service = build("calendar", "v3", credentials=creds)
    start = datetime.fromisoformat(task["due_date"])
    end = start + timedelta(hours=1)

    event_body = {
        "summary": task["title"],
        "description": task.get("description") or "Created by TaskFlow",
        "start": {"date": start.date().isoformat()},
        "end": {"date": end.date().isoformat()},
    }

    existing_event_id = task.get("google_event_id")
    if existing_event_id:
        event = service.events().update(
            calendarId="primary", eventId=existing_event_id, body=event_body
        ).execute()
    else:
        event = service.events().insert(calendarId="primary", body=event_body).execute()

    return {"synced": True, "event_id": event["id"]}


def pull_events_from_calendar(days_ahead: int = 14) -> list:
    """Fetch upcoming Google Calendar events so they can be shown/imported as tasks."""
    creds = _get_credentials()
    if not creds:
        return []

    service = build("calendar", "v3", credentials=creds)
    now = datetime.utcnow().isoformat() + "Z"
    later = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary", timeMin=now, timeMax=later,
        singleEvents=True, orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])
    return [
        {
            "id": e["id"],
            "title": e.get("summary", "(no title)"),
            "start": e["start"].get("dateTime", e["start"].get("date")),
        }
        for e in events
    ]
