"""
Browser Push Notifications — 100% free, no third-party service.
Uses the standard Web Push protocol (VAPID) that all browsers support natively.

VAPID keys are generated once and stored in the settings table. The public
key is exposed to the frontend so it can subscribe the browser; the private
key signs outgoing push messages. No external push provider (no Firebase,
no OneSignal) is required.
"""
import json
import base64
from py_vapid import Vapid01
from pywebpush import webpush, WebPushException
from database.db import get_db

VAPID_CLAIMS_EMAIL = "mailto:admin@taskflow.local"


def _get_setting(conn, key):
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else None


def _set_setting(conn, key, value):
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


def get_or_create_vapid_keys():
    conn = get_db()
    private_key = _get_setting(conn, "vapid_private_key")
    public_key = _get_setting(conn, "vapid_public_key")

    if not private_key or not public_key:
        vapid = Vapid01()
        vapid.generate_keys()
        private_key = vapid.private_pem().decode("utf-8")

        # Browsers expect the raw uncompressed EC point (0x04 || X || Y),
        # base64url-encoded with no padding, as the applicationServerKey.
        nums = vapid.public_key.public_numbers()
        raw = b"\x04" + nums.x.to_bytes(32, "big") + nums.y.to_bytes(32, "big")
        public_key = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")

        _set_setting(conn, "vapid_private_key", private_key)
        _set_setting(conn, "vapid_public_key", public_key)
        conn.commit()

    conn.close()
    return {"public_key": public_key, "private_key": private_key}


def save_subscription(member_id: str, subscription_info: dict):
    conn = get_db()
    _set_setting(conn, f"push_subscription:{member_id}", json.dumps(subscription_info))
    conn.commit()
    conn.close()


def get_all_subscriptions():
    conn = get_db()
    rows = conn.execute(
        "SELECT key, value FROM settings WHERE key LIKE 'push_subscription:%'"
    ).fetchall()
    conn.close()
    return [json.loads(r["value"]) for r in rows]


def send_push_to_all(title: str, body: str):
    keys = get_or_create_vapid_keys()
    subscriptions = get_all_subscriptions()
    results = []

    for sub in subscriptions:
        try:
            webpush(
                subscription_info=sub,
                data=json.dumps({"title": title, "body": body}),
                vapid_private_key=keys["private_key"],
                vapid_claims={"sub": VAPID_CLAIMS_EMAIL},
            )
            results.append({"endpoint": sub.get("endpoint", "")[:40], "sent": True})
        except WebPushException as e:
            results.append({"endpoint": sub.get("endpoint", "")[:40], "sent": False, "error": str(e)})

    return results
