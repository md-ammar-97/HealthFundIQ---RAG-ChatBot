import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, MatchAny,
)
from embeddings.schema import Chunk
from config.settings import settings
from ingestion.logger import get_logger

logger = get_logger("embeddings.store")

_CLIENT: QdrantClient | None = None
_COLLECTION_READY = False

# Embedding dimension — must match the model configured in settings
_VECTOR_DIM = 1024  # bge-large-en-v1.5; change to 384 if using bge-small


def _get_client() -> QdrantClient:
    global _CLIENT
    if _CLIENT is None:
        if settings.qdrant_url:
            _CLIENT = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key or None,
                timeout=30,
            )
            logger.info(f"Qdrant client connected: {settings.qdrant_url}")
        else:
            _CLIENT = QdrantClient(path=settings.qdrant_local_path)
            logger.info(f"Qdrant client using local path: {settings.qdrant_local_path}")
    return _CLIENT


def _ensure_collection() -> None:
    global _COLLECTION_READY
    if _COLLECTION_READY:
        return
    client = _get_client()
    existing = {c.name for c in client.get_collections().collections}
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=_VECTOR_DIM, distance=Distance.COSINE),
        )
        # Create payload indices for efficient filtered search
        for field in ("fund_id", "country", "section", "ticker", "isin",
                      "source_type", "domain_subcategory"):
            client.create_payload_index(
                collection_name=settings.qdrant_collection,
                field_name=field,
                field_schema="keyword",
            )
        logger.info(f"Created Qdrant collection '{settings.qdrant_collection}' with indices")
    else:
        logger.info(f"Qdrant collection '{settings.qdrant_collection}' exists")
    _COLLECTION_READY = True


def _chunk_to_point(chunk: Chunk) -> PointStruct:
    # Use UUID5 for deterministic, collision-free string IDs from chunk_id
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
    return PointStruct(
        id=point_id,
        vector=chunk.embedding,
        payload={
            "chunk_id": chunk.chunk_id,
            "fund_id": chunk.fund_id,
            "section": chunk.section,
            "country": chunk.country,
            "fund_name": chunk.fund_name,
            "ticker": chunk.ticker,
            "isin": chunk.isin,
            "domain_subcategory": chunk.domain_subcategory,
            "fund_type": chunk.fund_type,
            "source_type": chunk.source_type,
            "source_url": chunk.source_url,
            "official_url": chunk.official_url,
            "platform_url": chunk.platform_url,
            "last_updated_from_source": chunk.last_updated_from_source,
            "fetch_timestamp": chunk.fetch_timestamp,
            "text": chunk.text,
        },
    )


def upsert_chunks(chunks: list[Chunk]) -> tuple[int, int]:
    if not chunks:
        return 0, 0
    _ensure_collection()
    client = _get_client()

    points = []
    skipped = 0
    for chunk in chunks:
        if not chunk.embedding:
            skipped += 1
            continue
        points.append(_chunk_to_point(chunk))

    if not points:
        return 0, skipped

    try:
        # Qdrant upsert in batches of 100 to avoid payload size limits
        batch_size = 100
        for i in range(0, len(points), batch_size):
            client.upsert(
                collection_name=settings.qdrant_collection,
                points=points[i : i + batch_size],
                wait=True,
            )
        logger.info(f"Upserted {len(points)} chunks to Qdrant, skipped {skipped}")
        return len(points), skipped
    except Exception as e:
        logger.error(f"Qdrant upsert failed: {e}", exc_info=True)
        return 0, len(chunks)


def _build_filter(where: dict | None) -> Filter | None:
    """Convert ChromaDB-style where dict to Qdrant Filter."""
    if not where:
        return None

    must: list = []

    if "$and" in where:
        for cond in where["$and"]:
            must.extend(_parse_conditions(cond))
    else:
        must.extend(_parse_conditions(where))

    return Filter(must=must) if must else None


def _parse_conditions(cond: dict) -> list:
    conditions = []
    for key, value in cond.items():
        if key.startswith("$"):
            continue
        if isinstance(value, dict) and "$in" in value:
            conditions.append(FieldCondition(key=key, match=MatchAny(any=value["$in"])))
        else:
            conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
    return conditions


def query_collection(
    query_embedding: list[float],
    where: dict | None = None,
    n_results: int = 6,
) -> list[dict]:
    _ensure_collection()
    client = _get_client()
    qdrant_filter = _build_filter(where)

    try:
        results = client.search(
            collection_name=settings.qdrant_collection,
            query_vector=query_embedding,
            query_filter=qdrant_filter,
            limit=n_results,
            with_payload=True,
        )
        output = []
        for r in results:
            payload = r.payload or {}
            output.append({
                "chunk_id": payload.get("chunk_id", ""),
                "text": payload.get("text", ""),
                # Expose metadata under the same key the retriever/reranker expect
                "metadata": {k: v for k, v in payload.items() if k != "text"},
                # Convert cosine similarity (0–1, higher=better) → distance (lower=better)
                "distance": 1.0 - r.score,
            })
        return output
    except Exception as e:
        logger.error(f"Qdrant query failed: {e}", exc_info=True)
        return []


def get_collection_count() -> int:
    try:
        _ensure_collection()
        return _get_client().count(
            collection_name=settings.qdrant_collection, exact=True
        ).count
    except Exception:
        return 0
