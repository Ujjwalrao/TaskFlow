"""
Slack Import — reads recent channel messages and surfaces them as candidate tasks.

Setup (free, ~7 min):
  1. https://api.slack.com/apps -> "Create New App" -> "From scratch"
  2. "OAuth & Permissions" -> Bot Token Scopes: channels:history, chat:write, users:read
  3. "Install to Workspace" -> copy the Bot Token (xoxb-...)
  4. Invite the bot to the channel you want to read: /invite @your-bot-name
  5. Put in backend/.env:
       SLACK_BOT_TOKEN=
       SLACK_CHANNEL_ID=
"""
import os
import requests

BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID", "")


def is_configured() -> bool:
    return bool(BOT_TOKEN and CHANNEL_ID)


def fetch_recent_messages(limit: int = 20) -> list:
    if not is_configured():
        return []

    resp = requests.get(
        "https://slack.com/api/conversations.history",
        headers={"Authorization": f"Bearer {BOT_TOKEN}"},
        params={"channel": CHANNEL_ID, "limit": limit},
        timeout=10,
    )
    data = resp.json()
    if not data.get("ok"):
        return []

    return [
        {"slack_ts": m["ts"], "text": m.get("text", "")}
        for m in data.get("messages", [])
        if m.get("text")
    ]


def send_message(text: str):
    if not is_configured():
        return {"sent": False, "reason": "not configured"}
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {BOT_TOKEN}"},
        json={"channel": CHANNEL_ID, "text": text},
        timeout=10,
    )
    return resp.json()
