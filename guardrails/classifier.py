import re
from llm.groq_client import complete
from llm.prompt_builder import build_classifier_messages
from config.settings import settings
from ingestion.logger import get_logger

logger = get_logger("guardrails.classifier")

VALID_INTENTS = {"FACTUAL", "COMPARISON", "FUND_LIST", "AGGREGATION", "ADVICE", "OUT_OF_SCOPE"}

# Stage 1: High-confidence regex patterns for advice detection
# NOTE: "hold" is NOT standalone — must be in context of "buy/sell/hold"
ADVICE_PATTERNS = [
    re.compile(r"\bshould\s+i\b", re.IGNORECASE),
    re.compile(r"\bwhich\b.{0,30}\b(best|better|recommend)\b", re.IGNORECASE),
    re.compile(r"\b(buy|sell)\b(?!.*holdings)", re.IGNORECASE),   # "buy" but not "buyback in holdings"
    re.compile(r"\bbuy\s*/\s*sell\s*/\s*hold\b", re.IGNORECASE),  # "buy/sell/hold" together
    re.compile(r"\bportfolio\b(?!.*manager|.*manager)", re.IGNORECASE),
    re.compile(r"\b(returns?|performance)\b.{0,30}\b(predict|expect|forecast|next.year|going.to)\b", re.IGNORECASE),
    re.compile(r"\bhow.much.{0,20}(invest|put|allocate)\b", re.IGNORECASE),
    re.compile(r"\b(right|good|best)\s+time\b", re.IGNORECASE),
    re.compile(r"\brisk\s+profile\b", re.IGNORECASE),
    re.compile(r"\btax\s+(plan|advice|saving)\b", re.IGNORECASE),
    re.compile(r"\bshould\s+(i|we|you)\b", re.IGNORECASE),
    re.compile(r"\b(safest?|risky|dangerous)\s+(fund|etf|investment)\b", re.IGNORECASE),
    re.compile(r"\bwill\s+.{0,20}\b(go up|rise|grow|increase|perform|outperform)\b", re.IGNORECASE),
]

# PII patterns — detect before classification
PII_PATTERNS = [
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),    # PAN
    re.compile(r"\b[0-9]{12}\b"),                   # Aadhaar
    re.compile(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"),  # Email
]


def contains_pii(query: str) -> bool:
    return any(p.search(query) for p in PII_PATTERNS)


def classify(query: str) -> str:
    """
    Returns one of: FACTUAL, COMPARISON, ADVICE, OUT_OF_SCOPE.
    Two-stage: fast regex first, then LLM for ambiguous cases.
    """
    # Stage 1: fast regex
    for pattern in ADVICE_PATTERNS:
        if pattern.search(query):
            logger.info(f"Stage 1 ADVICE match on: {query[:60]!r}")
            return "ADVICE"

    # Stage 2: LLM classifier (only for non-obvious cases)
    messages = build_classifier_messages(query)
    result = complete(
        messages=messages,
        model=settings.groq_classifier_model,
        temperature=0.0,
        max_tokens=5,
    )

    if result:
        intent = result.strip().upper().split()[0]  # take first word only
        if intent in VALID_INTENTS:
            logger.info(f"Stage 2 classified as {intent}: {query[:60]!r}")
            return intent

    # Default to OUT_OF_SCOPE on unexpected classifier output
    logger.warning(f"Unexpected classifier result '{result}' — defaulting to OUT_OF_SCOPE")
    return "OUT_OF_SCOPE"
