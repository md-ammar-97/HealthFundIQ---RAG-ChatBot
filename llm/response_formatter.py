import re
from dataclasses import dataclass, field


PROHIBITED_PHRASES = [
    "is better", "is best", "you should", "i recommend", "i suggest",
    "top pick", "best fund", "safe investment", "guaranteed", "will go up",
    "will perform", "expected return",
]

REFUSAL_ADVICE = (
    "I can't provide investment advice or buy/sell recommendations. "
    "I can help with factual details such as expense ratio, AUM, benchmark, "
    "holdings, risk rating, investment objective, and official source documents. "
    "What factual information would you like to know?"
)

REFUSAL_OOS = (
    "HealthFundIQ only covers healthcare, pharma, biotech, and med-tech funds "
    "across India, USA, Canada, China/Hong Kong, Singapore, Japan, and the UK. "
    "I couldn't find a relevant fund question in your query. "
    "Try asking about expense ratio, AUM, benchmark, holdings, or risk rating."
)

MISSING_DATA = (
    "I could not find this information in the current source set."
)

SERVICE_UNAVAILABLE = (
    "The response service is temporarily unavailable. Please try again shortly."
)


@dataclass
class BotResponse:
    answer: str
    source_url: str | None
    platform_url: str | None
    last_updated: str | None
    fetch_timestamp: str | None
    is_refusal: bool
    intent: str
    chunks_used: list[str] = field(default_factory=list)
    missing_data: bool = False


def _normalize_markdown(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip internal evidence IDs if they slip through
    text = re.sub(r"\s*\[C\d+(?:,\s*C\d+)*\]", "", text)
    # Put headings on their own lines if model collapsed them inline
    text = re.sub(r"\s+(#{1,6}\s+)", r"\n\n\1", text)
    # Split bullet markers onto separate lines
    text = re.sub(r"\s+([•*-]\s+)", r"\n\1", text)
    # Convert • to standard Markdown bullet
    text = re.sub(r"(?m)^\s*•\s+", "- ", text)
    # Ensure blank line before and after headings
    text = re.sub(r"(?m)^\s*(#{1,6}\s+.+?)\s*$", r"\n\1\n", text)
    # Put Sources section on its own block
    text = re.sub(r"\s+(Sources?:)\s*", r"\n\n\1\n", text)
    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _check_prohibited(text: str) -> bool:
    """Returns True if prohibited ranking/advice language is detected."""
    t = text.lower()
    return any(phrase in t for phrase in PROHIBITED_PHRASES)


def format_response(
    llm_answer: str | None,
    chunks: list[dict],
    intent: str,
) -> BotResponse:
    if not llm_answer:
        return BotResponse(
            answer=SERVICE_UNAVAILABLE,
            source_url=None, platform_url=None,
            last_updated=None, fetch_timestamp=None,
            is_refusal=False, intent=intent,
            missing_data=True,
        )

    # Post-process: if prohibited advice/ranking language slipped through, swap with refusal
    if _check_prohibited(llm_answer):
        import logging
        logging.getLogger("llm.response_formatter").warning(
            "Prohibited phrase detected in LLM response — substituting safe refusal"
        )
        return BotResponse(
            answer=REFUSAL_ADVICE,
            source_url=None, platform_url=None,
            last_updated=None, fetch_timestamp=None,
            is_refusal=True, intent=intent,
        )

    # Extract best source from top chunk
    source_url = None
    platform_url = None
    last_updated = None
    fetch_ts = None
    chunk_ids = []

    if chunks:
        top = chunks[0]
        meta = top.get("metadata", {})
        source_url = meta.get("official_url") or meta.get("source_url") or meta.get("platform_url")
        platform_url = meta.get("platform_url")
        last_updated = meta.get("last_updated_from_source") or None
        fetch_ts = meta.get("fetch_timestamp")
        chunk_ids = [c.get("chunk_id", c.get("metadata", {}).get("fund_id", "")) for c in chunks]

    # Normalize empty strings to None
    if not source_url:
        source_url = None
    if not last_updated:
        last_updated = None
    if not fetch_ts:
        fetch_ts = None

    llm_answer = _normalize_markdown(llm_answer)

    return BotResponse(
        answer=llm_answer,
        source_url=source_url,
        platform_url=platform_url,
        last_updated=last_updated,
        fetch_timestamp=fetch_ts,
        is_refusal=False,
        intent=intent,
        chunks_used=chunk_ids,
        missing_data="could not find" in llm_answer.lower(),
    )


def refusal_response(intent: str) -> BotResponse:
    text = REFUSAL_ADVICE if intent == "ADVICE" else REFUSAL_OOS
    return BotResponse(
        answer=text,
        source_url=None, platform_url=None,
        last_updated=None, fetch_timestamp=None,
        is_refusal=True, intent=intent,
    )


def missing_data_response(intent: str = "FACTUAL") -> BotResponse:
    return BotResponse(
        answer=MISSING_DATA,
        source_url=None, platform_url=None,
        last_updated=None, fetch_timestamp=None,
        is_refusal=False, intent=intent,
        missing_data=True,
    )
