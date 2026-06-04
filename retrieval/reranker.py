def rerank(chunks: list[dict]) -> list[dict]:
    """
    Boost official-source chunks. Penalize chunks missing last_updated.
    Returns reranked list (in-place scoring, then sorted).
    """
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        score = chunk.get("distance", 1.0)  # lower distance = better in cosine

        # Boost official sources (reduce distance score = move up)
        if meta.get("source_type") == "official":
            score *= 0.85
        elif meta.get("source_type") == "pdf":
            score *= 0.92

        # Penalize stale / missing date
        if not meta.get("last_updated_from_source"):
            score *= 1.05

        chunk["rerank_score"] = score

    return sorted(chunks, key=lambda c: c["rerank_score"])
