import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from database.db import get_db

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("", methods=["GET"])
def list_goals():
    conn = get_db()
    rows = conn.execute("SELECT * FROM goals").fetchall()
    result = []
    for r in rows:
        g = dict(r)
        linked_tasks = conn.execute(
            "SELECT COUNT(*) c FROM tasks WHERE goal_id=?", (g["id"],)
        ).fetchone()["c"]
        done_tasks = conn.execute(
            "SELECT COUNT(*) c FROM tasks WHERE goal_id=? AND status='completed'", (g["id"],)
        ).fetchone()["c"]
        g["task_count"] = linked_tasks
        g["progress"] = int((done_tasks / linked_tasks) * 100) if linked_tasks else 0
        result.append(g)
    conn.close()
    return jsonify(result)


@goals_bp.route("", methods=["POST"])
def create_goal():
    data = request.get_json(silent=True) or {}
    conn = get_db()
    goal_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO goals (id, title, description, target_date, created_at) VALUES (?,?,?,?,?)",
        (goal_id, data.get("title"), data.get("description"), data.get("target_date"),
         datetime.utcnow().isoformat()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM goals WHERE id=?", (goal_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    conn = get_db()
    conn.execute("DELETE FROM goals WHERE id=?", (goal_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": goal_id})
