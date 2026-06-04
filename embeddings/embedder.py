from sentence_transformers import SentenceTransformer
from embeddings.schema import Chunk
from config.settings import settings
from ingestion.logger import get_logger
import numpy as np

logger = get_logger("embeddings.embedder")

_MODEL: SentenceTransformer | None = None

# multilingual-e5 requires explicit prefixes for asymmetric retrieval:
# queries get "query: ", corpus passages get "passage: ".
# These are no-ops for models that don't use instruction prefixes.
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _MODEL = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded")
    return _MODEL


def encode_query(query: str) -> list[float]:
    model = _get_model()
    vec = model.encode(QUERY_PREFIX + query, normalize_embeddings=True)
    return vec.tolist()


def encode_chunks(chunks: list[Chunk]) -> list[Chunk]:
    if not chunks:
        return []
    model = _get_model()
    texts = [PASSAGE_PREFIX + c.text for c in chunks]
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    valid = []
    for chunk, vec in zip(chunks, vecs):
        arr = np.array(vec)
        if np.any(np.isnan(arr)) or np.any(np.isinf(arr)):
            logger.error(f"Invalid embedding for chunk {chunk.chunk_id} — skipping")
            continue
        chunk.embedding = vec.tolist()
        valid.append(chunk)

    logger.info(f"Encoded {len(valid)}/{len(chunks)} chunks")
    return valid
