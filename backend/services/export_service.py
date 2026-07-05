"""
Export & Reporting — free, local, no API calls.
PDF generation via reportlab, CSV via Python's built-in csv module.
"""
import csv
import io
from datetime import date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_weekly_pdf(tasks: list, habits: list, member_stats: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    elements = []

    week_start = date.today() - timedelta(days=7)
    elements.append(Paragraph("Weekly Productivity Report", styles["Title"]))
    elements.append(Paragraph(f"{week_start.isoformat()} — {date.today().isoformat()}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    completed = [t for t in tasks if t.get("status") == "completed"]
    pending = [t for t in tasks if t.get("status") != "completed"]
    overdue = [t for t in pending if t.get("due_date") and t["due_date"] < date.today().isoformat()]

    summary_data = [
        ["Metric", "Value"],
        ["Tasks completed", str(len(completed))],
        ["Tasks pending", str(len(pending))],
        ["Tasks overdue", str(len(overdue))],
        ["Active habits tracked", str(len(habits))],
    ]
    summary_table = Table(summary_data, colWidths=[8 * cm, 6 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.7 * cm))

    if member_stats:
        elements.append(Paragraph("Team Performance", styles["Heading2"]))
        team_data = [["Member", "Completed", "Total", "Completion Rate"]]
        for m in member_stats:
            team_data.append([m["name"], str(m["completed_tasks"]), str(m["total_tasks"]), f"{m['completion_rate']}%"])
        team_table = Table(team_data, colWidths=[5 * cm, 3 * cm, 3 * cm, 4 * cm])
        team_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        elements.append(team_table)
        elements.append(Spacer(1, 0.7 * cm))

    if habits:
        elements.append(Paragraph("Habit Streaks", styles["Heading2"]))
        habit_data = [["Habit", "Current Streak", "Longest Streak"]]
        for h in habits:
            habit_data.append([h["title"], str(h["current_streak"]), str(h["longest_streak"])])
        habit_table = Table(habit_data, colWidths=[8 * cm, 4 * cm, 4 * cm])
        habit_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        elements.append(habit_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


def generate_csv(tasks: list) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "status", "priority", "due_date", "assignee_id", "completed_at"])
    for t in tasks:
        writer.writerow([
            t.get("id"), t.get("title"), t.get("status"), t.get("priority"),
            t.get("due_date"), t.get("assignee_id"), t.get("completed_at"),
        ])
    return buffer.getvalue().encode("utf-8")
