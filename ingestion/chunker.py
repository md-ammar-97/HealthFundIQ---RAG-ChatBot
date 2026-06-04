import re
from ingestion.normalizer import NormalizedFund
from embeddings.schema import Chunk, SECTION_LABELS
from ingestion.logger import get_logger

logger = get_logger("ingestion.chunker")

MAX_CHUNK_TOKENS = 512
MIN_CHUNK_CHARS = 80       # ~20 tokens
CHARS_PER_TOKEN = 4        # rough approximation


def _prefix(fund_name: str, country: str, section: str) -> str:
    label = SECTION_LABELS.get(section, section)
    return f"[{fund_name} | {country} | {label}]"


def _split_text(text: str, max_chars: int) -> list[str]:
    """Split text into parts without breaking mid-sentence."""
    if len(text) <= max_chars:
        return [text]
    parts = []
    while text:
        if len(text) <= max_chars:
            parts.append(text)
            break
        # Find last sentence boundary within limit
        chunk = text[:max_chars]
        boundary = max(chunk.rfind(". "), chunk.rfind(".\n"), chunk.rfind("; "))
        if boundary < max_chars // 2:
            boundary = max_chars
        parts.append(text[:boundary + 1].strip())
        text = text[boundary + 1:].strip()
    return [p for p in parts if p]


def _make_chunk(
    fund: NormalizedFund,
    section: str,
    content: str,
    part: int | None = None,
) -> Chunk | None:
    if not content or len(content) < MIN_CHUNK_CHARS:
        return None

    prefix = _prefix(fund.fund_name, fund.country_or_market, section)
    text = f"{prefix}\n{content}"
    chunk_id = f"{fund.fund_id}_{section}"
    if part is not None:
        chunk_id += f"_part{part}"

    return Chunk(
        chunk_id=chunk_id,
        section=section,
        text=text,
        fund_id=fund.fund_id,
        country=fund.country_or_market,
        fund_name=fund.fund_name,
        ticker=fund.ticker_or_identifier or "",
        isin="",  # for ETFs; UCITS isin stored in ticker_or_identifier
        domain_subcategory=fund.domain_subcategory,
        fund_type=fund.fund_type,
        source_type=fund.source_type,
        source_url=fund.official_url or fund.platform_url,
        official_url=fund.official_url or "",
        platform_url=fund.platform_url,
        last_updated_from_source=fund.last_updated_from_source or "",
        fetch_timestamp=fund.fetch_timestamp,
    )


def _make_chunks_from_text(
    fund: NormalizedFund,
    section: str,
    content: str,
) -> list[Chunk]:
    max_chars = MAX_CHUNK_TOKENS * CHARS_PER_TOKEN
    parts = _split_text(content, max_chars)
    chunks = []
    for i, part in enumerate(parts):
        part_num = i + 1 if len(parts) > 1 else None
        c = _make_chunk(fund, section, part, part_num)
        if c:
            chunks.append(c)
    return chunks


def chunk_fund(fund: NormalizedFund) -> list[Chunk]:
    chunks: list[Chunk] = []

    # -- overview (always created) --
    obj_snippet = (fund.investment_objective or "")[:100]
    overview_content = (
        f"{fund.fund_name} is a {fund.fund_type} in the {fund.domain_subcategory} category, "
        f"listed on {fund.exchange or 'N/A'}, currency {fund.currency}. "
        f"Country/Market: {fund.country_or_market}. "
        f"Fund house/issuer: {fund.fund_house_or_issuer or 'N/A'}. "
        + (f"Objective: {obj_snippet}..." if obj_snippet else "")
    )
    c = _make_chunk(fund, "overview", overview_content)
    if c:
        chunks.append(c)

    # -- identity --
    identity_content = (
        f"Ticker/Identifier: {fund.ticker_or_identifier or 'N/A'}. "
        f"Exchange: {fund.exchange or 'N/A'}. "
        f"Currency: {fund.currency}. "
        f"Fund type: {fund.fund_type}."
    )
    c = _make_chunk(fund, "identity", identity_content)
    if c:
        chunks.append(c)

    # -- cost_ratio --
    if fund.expense_ratio_or_mer_or_ter:
        content = (
            f"The expense ratio / MER / TER of {fund.fund_name} is "
            f"{fund.expense_ratio_or_mer_or_ter}."
        )
        chunks.extend(_make_chunks_from_text(fund, "cost_ratio", content))

    # -- risk --
    if fund.risk_rating_or_riskometer:
        content = (
            f"The risk rating / riskometer of {fund.fund_name} is "
            f"{fund.risk_rating_or_riskometer}."
        )
        chunks.extend(_make_chunks_from_text(fund, "risk", content))

    # -- benchmark --
    if fund.benchmark:
        content = f"The benchmark of {fund.fund_name} is: {fund.benchmark}."
        chunks.extend(_make_chunks_from_text(fund, "benchmark", content))

    # -- investment_objective --
    if fund.investment_objective:
        content = f"Investment objective of {fund.fund_name}: {fund.investment_objective}"
        chunks.extend(_make_chunks_from_text(fund, "investment_objective", content))

    # -- fund_management --
    if fund.fund_management:
        content = f"The fund manager / portfolio manager of {fund.fund_name} is {fund.fund_management}."
        chunks.extend(_make_chunks_from_text(fund, "fund_management", content))

    # -- fund_house_or_issuer --
    if fund.fund_house_or_issuer:
        content = f"The fund house / issuer / AMC of {fund.fund_name} is {fund.fund_house_or_issuer}."
        chunks.extend(_make_chunks_from_text(fund, "fund_house_or_issuer", content))

    # -- nav_or_price --
    if fund.nav_or_price:
        content = f"The current NAV / price of {fund.fund_name} is {fund.nav_or_price}."
        chunks.extend(_make_chunks_from_text(fund, "nav_or_price", content))

    # -- aum --
    if fund.aum:
        content = (
            f"The AUM / net assets / fund size of {fund.fund_name} is {fund.aum} "
            f"({fund.currency})."
        )
        chunks.extend(_make_chunks_from_text(fund, "aum", content))

    # -- top_10_holdings --
    if fund.top_10_holdings:
        lines = []
        for i, h in enumerate(fund.top_10_holdings[:10], 1):
            w = f" — {h['weight']}" if h.get("weight") else ""
            lines.append(f"{i}. {h['name']}{w}")
        content = f"Top 10 Holdings of {fund.fund_name}:\n" + "\n".join(lines)
        chunks.extend(_make_chunks_from_text(fund, "top_10_holdings", content))

    # -- sector_exposure --
    if fund.sector_exposure:
        lines = [f"{e['label']}: {e.get('weight', 'N/A')}" for e in fund.sector_exposure]
        content = f"Sector exposure of {fund.fund_name}:\n" + "\n".join(lines)
        chunks.extend(_make_chunks_from_text(fund, "sector_exposure", content))

    # -- geographic_exposure --
    if fund.geographic_exposure:
        lines = [f"{e['label']}: {e.get('weight', 'N/A')}" for e in fund.geographic_exposure]
        content = f"Geographic exposure of {fund.fund_name}:\n" + "\n".join(lines)
        chunks.extend(_make_chunks_from_text(fund, "geographic_exposure", content))

    # -- minimum_investment (includes SIP for India) --
    if fund.minimum_investment or fund.minimum_sip:
        parts = []
        if fund.minimum_sip:
            parts.append(f"Minimum SIP: {fund.minimum_sip}")
        if fund.minimum_investment:
            parts.append(f"Minimum lumpsum / investment: {fund.minimum_investment}")
        content = ". ".join(parts) + f" for {fund.fund_name}."
        chunks.extend(_make_chunks_from_text(fund, "minimum_investment", content))

    # -- exit_load --
    if fund.exit_load_or_redemption_fee:
        content = (
            f"Exit load / redemption fee of {fund.fund_name}: "
            f"{fund.exit_load_or_redemption_fee}."
        )
        chunks.extend(_make_chunks_from_text(fund, "exit_load", content))

    # -- distribution_policy --
    if fund.distribution_policy:
        content = (
            f"Distribution policy of {fund.fund_name}: {fund.distribution_policy}."
        )
        chunks.extend(_make_chunks_from_text(fund, "distribution_policy", content))

    # -- documents --
    if fund.documents:
        content = f"Documents for {fund.fund_name}: " + ", ".join(fund.documents)
        chunks.extend(_make_chunks_from_text(fund, "documents", content))

    logger.info(f"{fund.fund_id}: {len(chunks)} chunks created")
    return chunks
