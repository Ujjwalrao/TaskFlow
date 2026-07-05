"""
Semantic Search Engine — 100% free, 100% local.
Uses `sentence-transformers` (all-MiniLM-L6-v2, ~80MB) to embed text
directly on the CPU. No API key, no network call, no per-request cost.

This is the genuine ML component of the app (as opposed to prompt-wrapping
around a hosted LLM) — a real vector model producing real embeddings that
are compared with cosine similarity.
"""
import numpy as np
import pickle

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> bytes:
    model = get_model()
    vector = model.encode(text, convert_to_numpy=True)
    return pickle.dumps(vector)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


def semantic_search(query: str, candidates: list, top_k: int = 10) -> list:
    """
    candidates: list of dicts, each must have an "embedding" key (pickled bytes or None)
    and a "text" key (used as fallback if no embedding exists yet).
    Returns candidates sorted by similarity score, highest first.
    """
    model = get_model()
    query_vec = model.encode(query, convert_to_numpy=True)

    scored = []
    for item in candidates:
        if item.get("embedding"):
            item_vec = pickle.loads(item["embedding"])
        else:
            item_vec = model.encode(item.get("text", ""), convert_to_numpy=True)
        score = cosine_similarity(query_vec, item_vec)
        scored.append({**item, "score": round(score, 4)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
