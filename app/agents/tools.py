from typing import Optional

from app.retrieval.keyword_search import keyword_search
from app.retrieval.vector_store import load_vector_store

# Reciprocal Rank Fusion constant. 60 is the standard value: it keeps one
# list's top hit from drowning out the other list.
RRF_K = 60

# How many candidates each search contributes before the lists are merged.
CANDIDATE_MULTIPLIER = 3
MIN_CANDIDATES = 10


def _document_key(document) -> tuple:
    metadata = document.metadata

    return (
        metadata.get("source"),
        metadata.get("page"),
        metadata.get("section"),
        metadata.get("sheet"),
        metadata.get("row"),
        document.page_content.strip(),
    )


def search_documents(
    question: str,
    org_id: str,
    k: int = 8,
    allowed_sources: Optional[list[str]] = None,
) -> list:
    """
    Hybrid search: meaning-based (vector) plus exact-word (keyword) search,
    merged with Reciprocal Rank Fusion.

    Vector search finds passages that mean the same thing; keyword search
    finds passages containing the exact words — names, cities, IDs — that
    vector search tends to miss. A passage found by both ranks highest.
    """

    candidates = max(k * CANDIDATE_MULTIPLIER, MIN_CANDIDATES)

    vector_store = load_vector_store(org_id)

    search_filter = (
        {"source": {"$in": allowed_sources}} if allowed_sources else None
    )

    vector_results = vector_store.similarity_search_with_score(
        question,
        k=candidates,
        filter=search_filter,
    )

    keyword_results = keyword_search(
        question,
        org_id,
        k=candidates,
        allowed_sources=allowed_sources,
    )

    fused_scores: dict[tuple, float] = {}
    documents_by_key: dict[tuple, object] = {}

    for rank, (document, score) in enumerate(vector_results):
        key = _document_key(document)

        document.metadata["retrieval_score"] = score
        documents_by_key.setdefault(key, document)
        fused_scores[key] = fused_scores.get(key, 0.0) + 1 / (RRF_K + rank + 1)

    for rank, document in enumerate(keyword_results):
        key = _document_key(document)

        documents_by_key.setdefault(key, document)
        fused_scores[key] = fused_scores.get(key, 0.0) + 1 / (RRF_K + rank + 1)

    ranked_keys = sorted(
        fused_scores,
        key=lambda key: fused_scores[key],
        reverse=True,
    )

    return [documents_by_key[key] for key in ranked_keys[:k]]
