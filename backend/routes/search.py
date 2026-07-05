from flask import Blueprint, request, jsonify
from database.db import get_db
from services.embedding_service import semantic_search

search_bp = Blueprint("search", __name__)


@search_bp.route("", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    conn = get_db()
    candidates = []

    for row in conn.execute("SELECT id, title, description FROM tasks").fetchall():
        text = f"{row['title']} {row['description'] or ''}"
        candidates.append({"id": row["id"], "type": "task", "title": row["title"], "text": text, "embedding": None})

    for row in conn.execute("SELECT id, title FROM habits").fetchall():
        candidates.append({"id": row["id"], "type": "habit", "title": row["title"], "text": row["title"], "embedding": None})

    for row in conn.execute("SELECT id, title, description FROM goals").fetchall():
        text = f"{row['title']} {row['description'] or ''}"
        candidates.append({"id": row["id"], "type": "goal", "title": row["title"], "text": text, "embedding": None})

    for row in conn.execute("SELECT id, title, content FROM documents").fetchall():
        candidates.append({"id": row["id"], "type": "document", "title": row["title"],
                            "text": (row["content"] or "")[:2000], "embedding": row["embedding"]})

    conn.close()

    if not candidates:
        return jsonify([])

    try:
        results = semantic_search(query, candidates, top_k=15)
    except Exception as e:
        return jsonify({"error": f"Search model unavailable: {e}"}), 503

    # Only return results with a meaningful similarity signal
    results = [r for r in results if r["score"] > 0.2]
    for r in results:
        r.pop("embedding", None)
        r.pop("text", None)

    return jsonify(results)
