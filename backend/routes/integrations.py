"""
Integrations — external provider connections.
Each provider follows the same pattern: connect (auth URL) -> callback
(exchange code for token, store it) -> sync (push/pull data).
"""
from flask import Blueprint, redirect, request, jsonify
from database.db import get_db
from services import google_calendar_service as gcal
from services import outlook_service as outlook
from services import notion_service as notion
from services import slack_service as slack
from services import jira_service as jira

integrations_bp = Blueprint("integrations", __name__)


@integrations_bp.route("/google/status", methods=["GET"])
def google_status():
    return jsonify({
        "configured": gcal.is_configured(),
        "connected": gcal.is_connected() if gcal.is_configured() else False,
    })


@integrations_bp.route("/google/connect", methods=["GET"])
def google_connect():
    if not gcal.is_configured():
        return jsonify({"error": "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set in backend .env"}), 400
    return jsonify({"auth_url": gcal.get_auth_url()})


@integrations_bp.route("/google/callback", methods=["GET"])
def google_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "missing authorization code"}), 400
    gcal.exchange_code_for_token(code)
    # Redirect back to the frontend settings page after a successful connect
    return redirect("http://localhost:5173/settings?google=connected")


@integrations_bp.route("/google/sync", methods=["POST"])
def google_sync():
    if not gcal.is_connected():
        return jsonify({"error": "Google Calendar not connected yet"}), 400

    conn = get_db()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE due_date IS NOT NULL AND status != 'completed'"
    ).fetchall()
    conn.close()

    results = []
    for t in tasks:
        result = gcal.push_task_to_calendar(dict(t))
        results.append({"task_id": t["id"], **result})

    return jsonify({"synced_count": sum(1 for r in results if r["synced"]), "details": results})


@integrations_bp.route("/google/events", methods=["GET"])
def google_events():
    if not gcal.is_connected():
        return jsonify({"error": "Google Calendar not connected yet"}), 400
    return jsonify(gcal.pull_events_from_calendar())


# ---------------- Outlook Calendar ----------------

@integrations_bp.route("/outlook/status", methods=["GET"])
def outlook_status():
    return jsonify({
        "configured": outlook.is_configured(),
        "connected": outlook.is_connected() if outlook.is_configured() else False,
    })


@integrations_bp.route("/outlook/connect", methods=["GET"])
def outlook_connect():
    if not outlook.is_configured():
        return jsonify({"error": "OUTLOOK_CLIENT_ID / OUTLOOK_CLIENT_SECRET not set in backend .env"}), 400
    return jsonify({"auth_url": outlook.get_auth_url()})


@integrations_bp.route("/outlook/callback", methods=["GET"])
def outlook_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "missing authorization code"}), 400
    outlook.exchange_code_for_token(code)
    return redirect("http://localhost:5173/settings?outlook=connected")


@integrations_bp.route("/outlook/sync", methods=["POST"])
def outlook_sync():
    if not outlook.is_connected():
        return jsonify({"error": "Outlook Calendar not connected yet"}), 400
    conn = get_db()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE due_date IS NOT NULL AND status != 'completed'"
    ).fetchall()
    conn.close()
    results = [{"task_id": t["id"], **outlook.push_task_to_calendar(dict(t))} for t in tasks]
    return jsonify({"synced_count": sum(1 for r in results if r["synced"]), "details": results})


# ---------------- Notion ----------------

@integrations_bp.route("/notion/status", methods=["GET"])
def notion_status():
    return jsonify({"configured": notion.is_configured()})


@integrations_bp.route("/notion/import", methods=["POST"])
def notion_import():
    if not notion.is_configured():
        return jsonify({"error": "NOTION_API_KEY / NOTION_DATABASE_ID not set in backend .env"}), 400

    import uuid
    from datetime import datetime
    rows = notion.fetch_database_rows()
    conn = get_db()
    created = 0
    for row in rows:
        existing = conn.execute("SELECT id FROM tasks WHERE title=?", (row["title"],)).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO tasks (id, title, status, priority, created_at) VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), row["title"], "pending", "medium", datetime.utcnow().isoformat()),
            )
            created += 1
    conn.commit()
    conn.close()
    return jsonify({"imported": created, "total_found": len(rows)})


# ---------------- Slack ----------------

@integrations_bp.route("/slack/status", methods=["GET"])
def slack_status():
    return jsonify({"configured": slack.is_configured()})


@integrations_bp.route("/slack/import", methods=["POST"])
def slack_import():
    if not slack.is_configured():
        return jsonify({"error": "SLACK_BOT_TOKEN / SLACK_CHANNEL_ID not set in backend .env"}), 400
    messages = slack.fetch_recent_messages()
    return jsonify({"messages": messages})


# ---------------- Jira ----------------

@integrations_bp.route("/jira/status", methods=["GET"])
def jira_status():
    return jsonify({"configured": jira.is_configured()})


@integrations_bp.route("/jira/import", methods=["POST"])
def jira_import():
    if not jira.is_configured():
        return jsonify({"error": "JIRA_SITE_URL / JIRA_EMAIL / JIRA_API_TOKEN not set in backend .env"}), 400

    import uuid
    from datetime import datetime
    issues = jira.fetch_my_issues()
    conn = get_db()
    created = 0
    for issue in issues:
        existing = conn.execute("SELECT id FROM tasks WHERE title=?", (issue["title"],)).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO tasks (id, title, status, priority, created_at) VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), issue["title"], "pending", "medium", datetime.utcnow().isoformat()),
            )
            created += 1
    conn.commit()
    conn.close()
    return jsonify({"imported": created, "total_found": len(issues)})
