"""
Email Digest — free tier via Resend (100 emails/day, no credit card).

Setup (~3 min):
  1. https://resend.com -> sign up (free)
  2. "API Keys" -> "Create API Key"
  3. Put in backend/.env:
       RESEND_API_KEY=
       DIGEST_TO_EMAIL=your-email@example.com
       DIGEST_FROM_EMAIL=onboarding@resend.dev   (Resend's free shared sender,
                                                   works immediately with no
                                                   domain verification)
"""
import os
import requests
from datetime import date, timedelta
from database.db import get_db

API_KEY = os.environ.get("RESEND_API_KEY", "")
TO_EMAIL = os.environ.get("DIGEST_TO_EMAIL", "")
FROM_EMAIL = os.environ.get("DIGEST_FROM_EMAIL", "onboarding@resend.dev")


def is_configured() -> bool:
    return bool(API_KEY and TO_EMAIL)


def _build_digest_html() -> str:
    conn = get_db()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    completed = conn.execute(
        "SELECT title FROM tasks WHERE status='completed' AND completed_at >= ?", (week_ago,)
    ).fetchall()
    pending = conn.execute(
        "SELECT title, due_date FROM tasks WHERE status != 'completed' ORDER BY due_date"
    ).fetchall()
    habits = conn.execute("SELECT title, current_streak FROM habits").fetchall()
    conn.close()

    completed_html = "".join(f"<li>{t['title']}</li>" for t in completed) or "<li>None this week</li>"
    pending_html = "".join(
        f"<li>{t['title']} — due {t['due_date'] or 'no date'}</li>" for t in pending[:10]
    ) or "<li>Nothing pending 🎉</li>"
    habits_html = "".join(
        f"<li>{h['title']}: {h['current_streak']} day streak</li>" for h in habits
    ) or "<li>No habits tracked yet</li>"

    return f"""
    <div style="font-family: sans-serif; max-width: 500px;">
      <h2>Your TaskFlow Weekly Digest</h2>
      <h3>✅ Completed this week</h3>
      <ul>{completed_html}</ul>
      <h3>⏳ Pending tasks</h3>
      <ul>{pending_html}</ul>
      <h3>🔥 Habit streaks</h3>
      <ul>{habits_html}</ul>
    </div>
    """


def send_digest_email() -> dict:
    if not is_configured():
        return {"sent": False, "reason": "RESEND_API_KEY / DIGEST_TO_EMAIL not set in backend .env"}

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "from": FROM_EMAIL,
            "to": [TO_EMAIL],
            "subject": "Your TaskFlow Weekly Digest",
            "html": _build_digest_html(),
        },
        timeout=10,
    )
    if resp.ok:
        return {"sent": True, "id": resp.json().get("id")}
    return {"sent": False, "reason": resp.text}
