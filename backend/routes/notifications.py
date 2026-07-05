"""
Notifications — Telegram bot (100% free, no rate-limit cost, no paid tier).

Setup (user does this themselves, takes ~2 minutes):
  1. Open Telegram, message @BotFather, send /newbot, follow prompts.
  2. Copy the bot token BotFather gives you.
  3. Message your new bot once (so it can find your chat_id).
  4. Save both values in Settings inside the app.

Google/Outlook Calendar sync and Notion/Slack/Jira import are NOT wired here
because they require an OAuth app registered on YOUR account (Google Cloud
Console / Azure Portal / Notion integrations page) — only you can create
that and provide the client_id/client_secret. The integration code can be
added the moment those credentials exist.
"""
import requests
from flask import Blueprint, request, jsonify
from database.db import get_db
from services import push_service
from services import email_digest_service

notifications_bp = Blueprint("notifications", __name__)


def _get_setting(conn, key):
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else None


def _set_setting(conn, key, value):
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


@notifications_bp.route("/telegram/config", methods=["POST"])
def save_telegram_config():
    data = request.get_json(silent=True) or {}
    conn = get_db()
    _set_setting(conn, "telegram_bot_token", data.get("bot_token", ""))
    _set_setting(conn, "telegram_chat_id", data.get("chat_id", ""))
    conn.commit()
    conn.close()
    return jsonify({"saved": True})


@notifications_bp.route("/telegram/test", methods=["POST"])
def send_test_notification():
    conn = get_db()
    token = _get_setting(conn, "telegram_bot_token")
    chat_id = _get_setting(conn, "telegram_chat_id")
    conn.close()

    if not token or not chat_id:
        return jsonify({"error": "Telegram bot_token/chat_id not configured yet"}), 400

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": "✅ TaskFlow notifications are working!"},
            timeout=10,
        )
        return jsonify({"sent": resp.ok, "telegram_response": resp.json()})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


def send_telegram_message(text: str):
    """Internal helper other services can call, e.g. daily digest / overdue alerts."""
    conn = get_db()
    token = _get_setting(conn, "telegram_bot_token")
    chat_id = _get_setting(conn, "telegram_chat_id")
    conn.close()
    if not token or not chat_id:
        return False
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
        return True
    except requests.RequestException:
        return False


@notifications_bp.route("/push/vapid-public-key", methods=["GET"])
def get_vapid_public_key():
    keys = push_service.get_or_create_vapid_keys()
    return jsonify({"public_key": keys["public_key"]})


@notifications_bp.route("/push/subscribe", methods=["POST"])
def subscribe_push():
    data = request.get_json(silent=True) or {}
    member_id = data.get("member_id", "default")
    subscription = data.get("subscription")
    if not subscription:
        return jsonify({"error": "subscription payload required"}), 400
    push_service.save_subscription(member_id, subscription)
    return jsonify({"subscribed": True})


@notifications_bp.route("/push/test", methods=["POST"])
def test_push():
    results = push_service.send_push_to_all(
        "TaskFlow", "🔔 Push notifications are working!"
    )
    return jsonify({"results": results})


@notifications_bp.route("/email-digest/status", methods=["GET"])
def email_digest_status():
    return jsonify({"configured": email_digest_service.is_configured()})


@notifications_bp.route("/email-digest/send", methods=["POST"])
def email_digest_send():
    result = email_digest_service.send_digest_email()
    status = 200 if result.get("sent") else 400
    return jsonify(result), status
