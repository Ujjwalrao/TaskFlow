"""
Team/Collaboration — deliberately login-free.
A "member" here is just a display name + color used for task delegation
and per-person analytics. There is no password, no session, no auth token.
Anyone with access to this workspace can add themselves as a member.
"""
import uuid
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from database.db import get_db

workspace_bp = Blueprint("workspace", __name__)


@workspace_bp.route("/members", methods=["GET"])
def list_members():
    conn = get_db()
    rows = conn.execute("SELECT * FROM members").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@workspace_bp.route("/members", methods=["POST"])
def add_member():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    role = data.get("role", "member")
    if role not in ("admin", "member"):
        role = "member"

    conn = get_db()
    member_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO members (id, name, color, role, created_at) VALUES (?,?,?,?,?)",
        (member_id, name, data.get("color", "#4F46E5"), role, datetime.utcnow().isoformat()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@workspace_bp.route("/members/<member_id>/role", methods=["PATCH"])
def update_member_role(member_id):
    """
    Only an admin acting_as can change roles — since there is no login/session,
    the caller must pass their own member_id as `acting_as` to prove they are
    an admin. This keeps the "no signup" spirit while still gating the action.
    """
    data = request.get_json(silent=True) or {}
    acting_as = data.get("acting_as")
    new_role = data.get("role")
    if new_role not in ("admin", "member"):
        return jsonify({"error": "role must be 'admin' or 'member'"}), 400

    conn = get_db()
    actor = conn.execute("SELECT * FROM members WHERE id=?", (acting_as,)).fetchone()
    if not actor or actor["role"] != "admin":
        conn.close()
        return jsonify({"error": "only an admin can change roles"}), 403

    conn.execute("UPDATE members SET role=? WHERE id=?", (new_role, member_id))
    conn.commit()
    row = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    conn.close()
    return jsonify(dict(row))


@workspace_bp.route("/members/<member_id>", methods=["DELETE"])
def remove_member(member_id):
    acting_as = request.args.get("acting_as")
    conn = get_db()
    actor = conn.execute("SELECT * FROM members WHERE id=?", (acting_as,)).fetchone()
    if not actor or actor["role"] != "admin":
        conn.close()
        return jsonify({"error": "only an admin can remove members"}), 403
    conn.execute("DELETE FROM members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": member_id})


@workspace_bp.route("/analytics", methods=["GET"])
def team_analytics():
    """Per-member completion stats for a simple team dashboard."""
    conn = get_db()
    members = conn.execute("SELECT * FROM members").fetchall()
    result = []
    for m in members:
        total = conn.execute(
            "SELECT COUNT(*) c FROM tasks WHERE assignee_id=?", (m["id"],)
        ).fetchone()["c"]
        done = conn.execute(
            "SELECT COUNT(*) c FROM tasks WHERE assignee_id=? AND status='completed'", (m["id"],)
        ).fetchone()["c"]
        overdue = conn.execute(
            """SELECT COUNT(*) c FROM tasks
               WHERE assignee_id=? AND status!='completed'
               AND due_date IS NOT NULL AND due_date < ?""",
            (m["id"], date.today().isoformat()),
        ).fetchone()["c"]
        result.append({
            "member_id": m["id"],
            "name": m["name"],
            "color": m["color"],
            "total_tasks": total,
            "completed_tasks": done,
            "overdue_tasks": overdue,
            "completion_rate": round((done / total) * 100, 1) if total else 0.0,
        })
    conn.close()
    return jsonify(result)
