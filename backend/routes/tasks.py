import uuid
import json
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from database.db import get_db
from services.recurrence_service import compute_next_occurrence

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("", methods=["GET"])
def list_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY due_date ASC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@tasks_bp.route("", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    conn = get_db()
    task_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO tasks
           (id, title, description, status, priority, due_date, assignee_id,
            goal_id, recurrence_rule, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            task_id,
            data.get("title"),
            data.get("description"),
            data.get("status", "pending"),
            data.get("priority", "medium"),
            data.get("due_date"),
            data.get("assignee_id"),
            data.get("goal_id"),
            json.dumps(data["recurrence_rule"]) if data.get("recurrence_rule") else None,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@tasks_bp.route("/<task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return jsonify({"error": "not found"}), 404

    fields, values = [], []
    for key in ["title", "description", "status", "priority", "due_date", "assignee_id", "goal_id"]:
        if key in data:
            fields.append(f"{key}=?")
            values.append(data[key])

    completing_now = data.get("status") == "completed" and task["status"] != "completed"
    if completing_now:
        fields.append("completed_at=?")
        values.append(datetime.utcnow().isoformat())

    if fields:
        values.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()

    # If a recurring task is completed, auto-create the next occurrence
    if completing_now and task["recurrence_rule"]:
        next_due = compute_next_occurrence(task["recurrence_rule"], date.today())
        if next_due:
            new_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO tasks
                   (id, title, description, status, priority, due_date, assignee_id,
                    goal_id, recurrence_rule, recurrence_parent_id, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    new_id, task["title"], task["description"], "pending",
                    task["priority"], next_due, task["assignee_id"], task["goal_id"],
                    task["recurrence_rule"], task["recurrence_parent_id"] or task_id,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()

    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return jsonify(dict(row))


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": task_id})
