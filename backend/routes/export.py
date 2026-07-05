from flask import Blueprint, Response
from database.db import get_db
from services.export_service import generate_weekly_pdf, generate_csv

export_bp = Blueprint("export", __name__)


def _get_data():
    conn = get_db()
    tasks = [dict(r) for r in conn.execute("SELECT * FROM tasks").fetchall()]
    habits = [dict(r) for r in conn.execute("SELECT * FROM habits").fetchall()]

    members = conn.execute("SELECT * FROM members").fetchall()
    member_stats = []
    for m in members:
        total = conn.execute("SELECT COUNT(*) c FROM tasks WHERE assignee_id=?", (m["id"],)).fetchone()["c"]
        done = conn.execute(
            "SELECT COUNT(*) c FROM tasks WHERE assignee_id=? AND status='completed'", (m["id"],)
        ).fetchone()["c"]
        member_stats.append({
            "name": m["name"], "total_tasks": total, "completed_tasks": done,
            "completion_rate": round((done / total) * 100, 1) if total else 0.0,
        })
    conn.close()
    return tasks, habits, member_stats


@export_bp.route("/pdf", methods=["GET"])
def export_pdf():
    tasks, habits, member_stats = _get_data()
    pdf_bytes = generate_weekly_pdf(tasks, habits, member_stats)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=weekly_report.pdf"},
    )


@export_bp.route("/csv", methods=["GET"])
def export_csv():
    tasks, _, _ = _get_data()
    csv_bytes = generate_csv(tasks)
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks_export.csv"},
    )
