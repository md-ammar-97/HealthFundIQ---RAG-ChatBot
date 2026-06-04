import re
from embeddings.embedder import encode_query
from embeddings.store import query_collection
from ingestion.logger import get_logger

logger = get_logger("retrieval.retriever")

# Maps section-related query keywords to ChromaDB section keys
SECTION_HINTS = {
    r"expense.ratio|mer|ter|cost.ratio|management.fee|ongoing.charge": "cost_ratio",
    r"\brisk\b|riskometer|srri|risk.rating|risk.level": "risk",
    r"benchmark|index.tracked|tracks|follows": "benchmark",
    r"objective|purpose|what.does.*fund.do|investment.goal": "investment_objective",
    r"manager|managed.by|portfolio.manager|fund.manager": "fund_management",
    r"issuer|fund.house|amc|management.company": "fund_house_or_issuer",
    r"\bnav\b|price|market.price|net.asset.value": "nav_or_price",
    r"\baum\b|net.assets|fund.size|assets.under": "aum",
    r"holdings|top.10|largest.positions|what.does.*hold": "top_10_holdings",
    r"sector|allocation.breakdown|sector.exposure": "sector_exposure",
    r"geographic|country.allocation|regional": "geographic_exposure",
    r"minimum|min.investment|min.sip|sip.amount|lumpsum": "minimum_investment",
    r"exit.load|redemption.fee|exit.charge": "exit_load",
    r"distribution|dividend|accumulating|distributing": "distribution_policy",
    r"document|factsheet|prospectus|fund.facts": "documents",
}

# Map ticker symbols to fund IDs (auto-built at first use from ChromaDB metadata)
_TICKER_MAP: dict[str, str] = {}

# Country name normalization
COUNTRY_MAP = {
    "india": "India", "indian": "India",
    "usa": "USA", "us": "USA", "united states": "USA", "american": "USA",
    "canada": "Canada", "canadian": "Canada",
    "china": "China/HK", "hong kong": "China/HK", "hk": "China/HK",
    "china/hk": "China/HK",
    "japan": "Japan", "japanese": "Japan",
    "singapore": "Singapore",
    "uk": "UK/Europe", "europe": "UK/Europe", "united kingdom": "UK/Europe",
    "uk/europe": "UK/Europe",
}


def _normalize_country(raw: str | None) -> str | None:
    if not raw:
        return None
    return COUNTRY_MAP.get(raw.lower().strip())


def _extract_entities(query: str) -> dict:
    """Extract ticker, country hint, and section hint from query text."""
    entities = {"ticker": None, "country": None, "section": None}

    # Ticker: uppercase 2–5 char word or HK numeric ticker
    ticker_match = re.search(
        r"\b([A-Z]{2,5})\b|\b([0-9]{4}\.[A-Z]{1,2})\b", query
    )
    if ticker_match:
        entities["ticker"] = (ticker_match.group(1) or ticker_match.group(2)).upper()

    # Country
    query_lower = query.lower()
    for key, val in COUNTRY_MAP.items():
        if key in query_lower:
            entities["country"] = val
            break

    # Section hint
    for pattern, section in SECTION_HINTS.items():
        if re.search(pattern, query, re.IGNORECASE):
            entities["section"] = section
            break

    return entities


def retrieve(
    query: str,
    country: str | None = None,         # from UI dropdown (pre-normalized)
    fund_id: str | None = None,          # from UI dropdown
    section_override: str | None = None, # for internal use
    top_k: int = 6,
) -> list[dict]:
    """
    Main retrieval function. Returns a list of chunk dicts with text + metadata.
    """
    entities = _extract_entities(query)

    # Build ChromaDB where clause
    # Priority: fund_id > ticker > country
    where: dict = {}
    filters = []

    if fund_id:
        filters.append({"fund_id": fund_id})
    elif entities.get("ticker"):
        filters.append({"ticker": entities["ticker"]})

    # Country: UI dropdown takes priority over query extraction
    effective_country = _normalize_country(country) or entities.get("country")
    if effective_country and not fund_id and not entities.get("ticker"):
        filters.append({"country": effective_country})

    # Section
    effective_section = section_override or entities.get("section")
    if effective_section:
        filters.append({"section": effective_section})

    if len(filters) == 1:
        where = filters[0]
    elif len(filters) > 1:
        where = {"$and": filters}

    embedding = encode_query(query)
    results = query_collection(
        query_embedding=embedding,
        where=where if where else None,
        n_results=top_k,
    )

    # If no results with tight filter, relax to country-only or no filter
    if not results and where:
        logger.info(f"No results with filter {where} — relaxing to country-only")
        relaxed_where = {"country": effective_country} if effective_country else None
        results = query_collection(
            query_embedding=embedding,
            where=relaxed_where,
            n_results=top_k,
        )

    logger.info(f"Retrieved {len(results)} chunks for query: {query[:60]!r}")
    return results
