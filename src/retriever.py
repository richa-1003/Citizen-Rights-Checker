# src/retriever.py
# 3-hop agentic retrieval from the Constitution vector store

# src/retriever.py
# Uses ChromaDB directly — no langchain-community (fixes proxies error)

# src/retriever.py
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "law-ai/InLegalBERT"

_collection = None

# Articles that are definitional/procedural — rarely the primary right
# in a citizen dispute. Often retrieved incorrectly due to keyword overlap.
RARELY_PRIMARY = {
    "12",    # Definition of "State" — not a right itself
    "13",    # Laws inconsistent with rights — procedural
    "31",    # Repealed property article
    "36",    # Definition clause of Part IV
    "37",    # DPSP not enforceable in court — not a right
}


def _get_collection():
    global _collection
    if _collection is None:
        ef = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_or_create_collection(
            name="constitution",
            embedding_function=ef
        )
    return _collection


def _parse(results: dict, threshold: float = 1.2) -> list:
    """
    Parse ChromaDB query results into a clean list of dicts.
    Filters out chunks with distance above threshold (too dissimilar).
    """
    out = []
    docs      = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    for doc, dist, meta in zip(docs, distances, metadatas):
        if dist < threshold:
            out.append({
                "text":           doc,
                "score":          round(dist, 3),
                "page":           meta.get("page"),
                "article_number": meta.get("article_number", ""),
                "article_title":  meta.get("article_title", ""),
                "part":           meta.get("part", ""),
            })
    return out


def _filter_irrelevant(results: list) -> list:
    """
    Remove definitional/procedural articles that are almost never
    the primary right in a citizen dispute.
    Falls back to original list if filtering leaves fewer than 2 results.
    """
    filtered = [
        r for r in results
        if r.get("article_number", "").rstrip(".") not in RARELY_PRIMARY
    ]
    return filtered if len(filtered) >= 2 else results


def _deduplicate(results: list) -> list:
    """
    Remove duplicate article numbers — keep only the highest-scoring
    chunk per article. Prevents the same article appearing twice.
    """
    seen = {}
    for r in results:
        art = r.get("article_number", "")
        if art not in seen:
            seen[art] = r
        else:
            # Keep the one with lower distance score (more similar)
            if r["score"] < seen[art]["score"]:
                seen[art] = r
    return list(seen.values())


def retrieve_rights(situation: str) -> dict:
    """
    3-hop agentic retrieval over the Constitution of India.

    Hop 1 — Fundamental Rights (Part III) most relevant to situation
    Hop 2 — State duties / Directive Principles if state action involved
    Hop 3 — Always retrieve Article 32 remedies

    Returns a dict consumed by generator.py
    """
    col = _get_collection()

    # ── Hop 1 — Fundamental Rights ──────────────────────────
    # Request more results than needed so filtering still leaves enough
    hop1_raw = col.query(
        query_texts=[f"fundamental rights violated when {situation}"],
        n_results=6
    )
    hop1 = _deduplicate(
        _filter_irrelevant(
            _parse(hop1_raw, threshold=1.2)
        )
    )
    # Keep top 3 after deduplication
    hop1 = hop1[:3]

    # ── Hop 2 — State duties ────────────────────────────────
    hop2_raw = col.query(
        query_texts=[f"state government duty obligation citizen {situation}"],
        n_results=3
    )
    hop2 = _deduplicate(
        _filter_irrelevant(
            _parse(hop2_raw, threshold=1.1)  # stricter threshold for hop 2
        )
    )
    hop2 = hop2[:2]

    # ── Hop 3 — Article 32 remedies (always) ───────────────
    hop3_raw = col.query(
        query_texts=[
            "Article 32 right constitutional remedies writ "
            "habeas corpus mandamus certiorari Supreme Court"
        ],
        n_results=2
    )
    # Looser threshold — we always want Art 32 even if not closest match
    hop3 = _parse(hop3_raw, threshold=1.8)
    hop3 = hop3[:2]

    # ── Confidence score ────────────────────────────────────
    # Based on best match score from hop1
    # Lower ChromaDB distance = higher similarity = higher confidence
    confidence = 0.0
    if hop1:
        best_score = hop1[0]["score"]
        confidence = round(max(0, (1.5 - best_score) / 1.5) * 100, 1)

    return {
        "fundamental_rights": hop1,
        "state_duties":       hop2,
        "remedies":           hop3,
        "confidence":         confidence,
        "situation":          situation
    }