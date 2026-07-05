import uuid
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from database.db import get_db
from services.recurrence_service import calculate_streak

habits_bp = Blueprint("habits", __name__)


@habits_bp.route("", methods=["GET"])
def list_habits():
    conn = get_db()
    rows = conn.execute("SELECT * FROM habits").fetchall()
    result = []
    for r in rows:
        h = dict(r)
        logs = conn.execute(
            "SELECT logged_date FROM habit_logs WHERE habit_id=? ORDER BY logged_date",
            (h["id"],),
        ).fetchall()
        h["logged_dates"] = [l["logged_date"] for l in logs]
        result.append(h)
    conn.close()
    return jsonify(result)


@habits_bp.route("", methods=["POST"])
def create_habit():
    data = request.get_json(silent=True) or {}
    conn = get_db()
    habit_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO habits (id, title, frequency, target_per_period, assignee_id, created_at)
           VALUES (?,?,?,?,?,?)""",
        (
            habit_id, data.get("title"), data.get("frequency", "daily"),
            data.get("target_per_period", 1), data.get("assignee_id"),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@habits_bp.route("/<habit_id>/log", methods=["POST"])
def log_habit(habit_id):
    """Mark a habit as done for a given day (defaults to today) and recompute streak."""
    data = request.get_json(silent=True) or {}
    log_date = data.get("date", date.today().isoformat())

    conn = get_db()
    habit = conn.execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
    if not habit:
        conn.close()
        return jsonify({"error": "not found"}), 404

    existing = conn.execute(
        "SELECT id FROM habit_logs WHERE habit_id=? AND logged_date=?",
        (habit_id, log_date),
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO habit_logs (id, habit_id, logged_date, created_at) VALUES (?,?,?,?)",
            (str(uuid.uuid4()), habit_id, log_date, datetime.utcnow().isoformat()),
        )
        conn.commit()

    logs = conn.execute(
        "SELECT logged_date FROM habit_logs WHERE habit_id=?", (habit_id,)
    ).fetchall()
    streak_info = calculate_streak([l["logged_date"] for l in logs], habit["frequency"])

    conn.execute(
        "UPDATE habits SET current_streak=?, longest_streak=? WHERE id=?",
        (streak_info["current_streak"], streak_info["longest_streak"], habit_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
    conn.close()
    return jsonify(dict(row))


@habits_bp.route("/<habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    conn = get_db()
    conn.execute("DELETE FROM habits WHERE id=?", (habit_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": habit_id})
