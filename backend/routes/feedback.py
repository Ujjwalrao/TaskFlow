"""
Feedback Loop — the "real learning" piece.
Every time the app suggests something (e.g. "move this task to Thursday",
"you might be overloaded, reschedule X"), the frontend logs whether the
user accepted or rejected it here. Over time this builds a per-suggestion-type
acceptance rate, which is used to boost or suppress that suggestion type
in future — a lightweight, transparent form of preference learning
(no black-box model, fully explainable).
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from database.db import get_db

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("", methods=["POST"])
def record_feedback():
    data = request.get_json(silent=True) or {}
    conn = get_db()
    fb_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO ai_feedback (id, suggestion_type, suggestion_text, accepted, created_at) VALUES (?,?,?,?,?)",
        (
            fb_id, data.get("suggestion_type"), data.get("suggestion_text"),
            1 if data.get("accepted") else 0, datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"id": fb_id, "recorded": True}), 201


@feedback_bp.route("/weights", methods=["GET"])
def get_suggestion_weights():
    """
    Returns an acceptance-rate weight (0.0 - 1.0) per suggestion_type,
    computed from historical feedback. The rescue/planning agents can use
    this to prioritize suggestion types the user tends to accept.
    """
    conn = get_db()
    rows = conn.execute(
        """SELECT suggestion_type,
                  AVG(accepted) as acceptance_rate,
                  COUNT(*) as sample_size
           FROM ai_feedback
           GROUP BY suggestion_type"""
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
