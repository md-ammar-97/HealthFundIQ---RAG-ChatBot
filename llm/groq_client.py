import time
from groq import Groq, APIStatusError, APIConnectionError
from config.settings import settings
from ingestion.logger import get_logger

logger = get_logger("llm.groq_client")

_CLIENT: Groq | None = None
MAX_RETRIES = 3
BACKOFF_BASE = 2


def _get_client() -> Groq:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = Groq(api_key=settings.groq_api_key)
    return _CLIENT


def complete(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> str | None:
    client = _get_client()
    model = model or settings.groq_model

    for attempt in range(MAX_RETRIES):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()
        except APIStatusError as e:
            if e.status_code == 429:
                wait = BACKOFF_BASE ** attempt
                logger.warning(f"Groq rate limit — waiting {wait}s")
                time.sleep(wait)
            else:
                logger.error(f"Groq API error {e.status_code}: {e.message}")
                return None
        except APIConnectionError as e:
            logger.error(f"Groq connection error: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_BASE ** attempt)
            else:
                return None
        except Exception as e:
            logger.error(f"Unexpected Groq error: {e}", exc_info=True)
            return None

    return None
