"""
Persistence layer for NormalizedFund → data/parsed/{country}/{fund_id}.json

The JSON file is the authoritative clean data source fed to the chunker/embedder.
raw_fields are excluded — only the normalized, human-readable fields are saved.
"""
import json
from dataclasses import asdict
from pathlib import Path
from ingestion.normalizer import NormalizedFund
from ingestion.logger import get_logger

logger = get_logger("ingestion.parsed_store")

PARSED_DIR = Path("data/parsed")

# Fields excluded from JSON — too noisy, not useful to the chatbot
_EXCLUDE = {"raw_fields"}


def _country_slug(country: str) -> str:
    return country.lower().replace("/", "_").replace(" ", "_")


def parsed_path(fund_id: str, country: str) -> Path:
    return PARSED_DIR / _country_slug(country) / f"{fund_id}.json"


def save_parsed(fund: NormalizedFund) -> Path:
    """Serialize NormalizedFund to JSON. Returns the file path written."""
    path = parsed_path(fund.fund_id, fund.country_or_market)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(fund)
    for field in _EXCLUDE:
        data.pop(field, None)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"{fund.fund_id}: saved parsed JSON to {path}")
    return path


def load_parsed(fund_id: str, country: str) -> NormalizedFund | None:
    """Load a NormalizedFund from its JSON file. Returns None if not found."""
    path = parsed_path(fund_id, country)
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["raw_fields"] = {}  # required by dataclass but not stored
    try:
        return NormalizedFund(**data)
    except TypeError as e:
        logger.error(f"{fund_id}: JSON schema mismatch — {e}")
        return None


def list_parsed() -> list[Path]:
    """Return all existing parsed JSON file paths."""
    return sorted(PARSED_DIR.rglob("*.json"))
