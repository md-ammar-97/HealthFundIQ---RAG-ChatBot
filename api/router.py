import re
import json
import yaml
from pathlib import Path
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
from api.models import ChatRequest, ChatResponse, FundListItem, FundDetails, HealthResponse
from guardrails.classifier import classify, contains_pii
from retrieval.retriever import retrieve
from retrieval.reranker import rerank
from llm.prompt_builder import build_messages
from llm.groq_client import complete
from llm.response_formatter import (
    format_response, refusal_response, missing_data_response,
)
from embeddings.store import get_collection_count
from config.settings import settings
from ingestion.logger import get_logger

logger = get_logger("api.router")
IST = timezone(timedelta(hours=5, minutes=30))

router = APIRouter()

# Cosine distance threshold below which a chunk is considered "directly relevant".
# Chunks at or above this threshold are too distant to count toward the confidence gate.
CONFIDENCE_THRESHOLD = 0.75

VALID_COUNTRIES = {
    "India", "USA", "Canada", "China/HK", "Japan", "Singapore", "UK/Europe"
}

_COUNTRY_TO_SLUG = {
    "India": "india",
    "USA": "usa",
    "Canada": "canada",
    "China/HK": "china_hk",
    "Japan": "japan",
    "Singapore": "singapore",
    "UK/Europe": "uk_europe",
}


def _load_funds() -> list[dict]:
    with open("config/sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["funds"]


_COUNTRY_ALIASES: dict[str, str] = {
    "india": "India",
    "usa": "USA",
    "united states": "USA",
    "america": "USA",
    "canada": "Canada",
    "china": "China/HK",
    "hong kong": "China/HK",
    "china/hk": "China/HK",
    "japan": "Japan",
    "singapore": "Singapore",
    "uk": "UK/Europe",
    "europe": "UK/Europe",
    "united kingdom": "UK/Europe",
    "britain": "UK/Europe",
}

_FUND_LIST_KEYWORDS = [
    "list all funds", "show all funds", "all funds",
    "funds from", "funds in", "funds available",
    "available funds", "what funds", "which funds",
    "how many funds", "funds do you have", "funds do we have",
    "funds are there", "show funds", "list funds",
    "funds here", "funds you have", "funds we have",
]

_TOTAL_AUM_KEYWORDS = [
    "total value", "total aum", "combined aum",
    "sum of aum", "aggregate aum", "total assets",
    "combined assets", "total fund value",
]


# Maps query keyword → (NormalizedFund field name, human-readable label)
_FACTUAL_FIELD_MAP: dict[str, tuple[str, str]] = {
    "expense ratio": ("expense_ratio_or_mer_or_ter", "Expense Ratio / TER / MER"),
    "total expense ratio": ("expense_ratio_or_mer_or_ter", "Expense Ratio / TER / MER"),
    "mer": ("expense_ratio_or_mer_or_ter", "MER / Expense Ratio"),
    "ter": ("expense_ratio_or_mer_or_ter", "TER / Expense Ratio"),
    "management expense ratio": ("expense_ratio_or_mer_or_ter", "Management Expense Ratio"),
    "assets under management": ("aum", "AUM / Net Assets"),
    "net assets": ("aum", "AUM / Net Assets"),
    "aum": ("aum", "AUM / Net Assets"),
    "benchmark": ("benchmark", "Benchmark"),
    "fund manager": ("fund_management", "Fund Manager"),
    "fund management": ("fund_management", "Fund Manager"),
    "manager": ("fund_management", "Fund Manager"),
    "fund house": ("fund_house_or_issuer", "Fund House / Issuer"),
    "issuer": ("fund_house_or_issuer", "Fund House / Issuer"),
    "risk rating": ("risk_rating_or_riskometer", "Risk Rating"),
    "riskometer": ("risk_rating_or_riskometer", "Risk Rating"),
    "risk level": ("risk_rating_or_riskometer", "Risk Level"),
    "minimum investment": ("minimum_investment", "Minimum Investment"),
    "min investment": ("minimum_investment", "Minimum Investment"),
    "minimum sip": ("minimum_sip", "Minimum SIP"),
    "exit load": ("exit_load_or_redemption_fee", "Exit Load"),
    "redemption fee": ("exit_load_or_redemption_fee", "Redemption Fee"),
    "nav": ("nav_or_price", "NAV / Price"),
    "net asset value": ("nav_or_price", "NAV / Net Asset Value"),
    "investment objective": ("investment_objective", "Investment Objective"),
    "fund objective": ("investment_objective", "Investment Objective"),
    "distribution policy": ("distribution_policy", "Distribution Policy"),
    "dividend policy": ("distribution_policy", "Distribution Policy"),
}


def _detect_factual_field(query: str) -> tuple[str, str] | None:
    """Return (field_name, label) for the most specific matching keyword, or None."""
    q = query.lower()
    # Sort by length descending so "expense ratio" matches before "ratio"
    for kw in sorted(_FACTUAL_FIELD_MAP, key=len, reverse=True):
        if kw in q:
            return _FACTUAL_FIELD_MAP[kw]
    return None


def _detect_fund(query: str, funds: list[dict]) -> dict | None:
    """Return the best-matching active fund dict from the query, or None."""
    q_lower = query.lower()
    active = [f for f in funds if not f.get("is_backup", False)]

    # 1. Exact ticker word match (higher precision)
    for fund in active:
        ticker = fund.get("ticker")
        if ticker:
            # Match ticker as a whole word (case-insensitive)
            if re.search(r"\b" + re.escape(ticker.upper()) + r"\b", query.upper()):
                return fund

    # 2. Substring match on fund_name — longest match wins
    matches = []
    for fund in active:
        name = fund["fund_name"].lower()
        # Try progressively shorter prefixes of the fund name
        words = name.split()
        for n in range(len(words), 1, -1):
            prefix = " ".join(words[:n])
            if prefix in q_lower:
                matches.append((n, fund))
                break

    if matches:
        matches.sort(key=lambda x: x[0], reverse=True)
        return matches[0][1]

    return None


def _structured_lookup(query: str, funds: list[dict]) -> "ChatResponse | None":
    """
    Deterministic lookup for factual fund-field questions.
    Returns a ChatResponse if a field value is found in the parsed JSON,
    or None to fall through to RAG retrieval.
    """
    field_info = _detect_factual_field(query)
    if not field_info:
        return None
    field_name, field_label = field_info

    fund = _detect_fund(query, funds)
    if not fund:
        return None

    country = fund["country"]
    fund_id = fund["id"]
    slug = _COUNTRY_TO_SLUG.get(country)
    if not slug:
        return None

    path = Path("data/parsed") / slug / f"{fund_id}.json"
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    value = data.get(field_name)
    if not value:
        return None

    source_url = data.get("official_url") or data.get("platform_url")
    last_updated = data.get("last_updated_from_source")
    fetch_timestamp = data.get("fetch_timestamp")
    answer = f"**{fund['fund_name']}** — {field_label}: **{value}**"
    logger.info(f"Structured lookup hit: {fund_id}.{field_name} = {value}")
    return ChatResponse(
        answer=answer,
        source_url=source_url,
        platform_url=data.get("platform_url"),
        last_updated=last_updated,
        fetch_timestamp=fetch_timestamp,
        is_refusal=False,
        intent="FACTUAL",
        missing_data=False,
        fund_name=fund["fund_name"],
    )


def _extract_country_from_query(query: str) -> str | None:
    q = query.lower()
    for key, value in _COUNTRY_ALIASES.items():
        if key in q:
            return value
    return None


def _is_fund_list_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in _FUND_LIST_KEYWORDS)


def _is_total_aum_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in _TOTAL_AUM_KEYWORDS)


def _parse_aum_crores(aum_str: str) -> float | None:
    """Parse Indian AUM strings like '₹2,158.58 Cr' → float crores. Returns None if unparseable."""
    if not aum_str:
        return None
    s = aum_str.replace("₹", "").replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*[Cc]r", s)
    return float(m.group(1)) if m else None


def _country_total_aum(country: str, funds: list[dict]) -> "ChatResponse":
    slug = _COUNTRY_TO_SLUG.get(country)
    if not slug:
        return ChatResponse(
            answer="I could not find this information in the current source set.",
            is_refusal=False, intent="AGGREGATION", missing_data=True,
        )

    active = [f for f in funds if not f.get("is_backup", False)]
    values, no_data = [], []

    for fund in active:
        path = Path("data/parsed") / slug / f"{fund['id']}.json"
        if not path.exists():
            no_data.append(fund["fund_name"])
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        aum = data.get("aum")
        currency = data.get("currency") or fund.get("currency", "")
        if aum:
            values.append({"fund_name": fund["fund_name"], "aum": aum, "currency": currency})
        else:
            no_data.append(fund["fund_name"])

    if not values:
        return ChatResponse(
            answer="I could not find AUM data for any fund in this market.",
            is_refusal=False, intent="AGGREGATION", missing_data=True,
        )

    # India: parse crore values and sum
    if country == "India":
        parseable, unparseable, total_cr = [], [], 0.0
        for v in values:
            cr = _parse_aum_crores(v["aum"])
            if cr is not None:
                total_cr += cr
                parseable.append(f"- {v['fund_name']}: {v['aum']}")
            else:
                unparseable.append(f"- {v['fund_name']}: {v['aum']}")

        if not parseable:
            return ChatResponse(
                answer="I could not calculate a total — AUM values are not in a parseable format.",
                is_refusal=False, intent="AGGREGATION", missing_data=False,
            )

        lines = [f"## Total AUM — {country} Healthcare Funds\n",
                 f"**Combined AUM (source-backed):** ₹{total_cr:,.2f} Cr\n",
                 "### Individual Fund AUM\n"] + parseable
        if unparseable:
            lines += ["\n### AUM Available (not summed)\n"] + unparseable
        if no_data:
            lines += ["\n### No AUM Data\n"] + [f"- {n}" for n in no_data]
        return ChatResponse(answer="\n".join(lines), is_refusal=False, intent="AGGREGATION", missing_data=False)

    # Other countries: list individual values without cross-currency sum
    currencies = {v["currency"] for v in values}
    lines = [f"## AUM by Fund — {country} Healthcare Funds\n"]
    if len(currencies) > 1:
        lines.append("*AUM values are in different currencies and cannot be summed.*\n")
    lines.append("### Fund AUM\n")
    for v in values:
        lines.append(f"- **{v['fund_name']}**: {v['aum']} ({v['currency']})")
    if no_data:
        lines += ["\n### No AUM Data\n"] + [f"- {n}" for n in no_data]
    return ChatResponse(answer="\n".join(lines), is_refusal=False, intent="AGGREGATION", missing_data=False)


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(IST).isoformat(),
        corpus_chunks=get_collection_count(),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # PII check (server-side safety net — primary check is client-side)
    if contains_pii(req.query):
        logger.warning("PII detected in query — refusing")
        return ChatResponse(
            answer="Please do not share personal information. HealthFundIQ only uses public fund sources.",
            is_refusal=True, intent="PII_DETECTED",
        )

    # Extract country from query text if not provided by the client
    if not req.country:
        req.country = _extract_country_from_query(req.query)

    # Validate country filter
    if req.country and req.country not in VALID_COUNTRIES:
        req.country = None

    # Short-circuit: fund listing — use structured YAML, skip RAG entirely
    if _is_fund_list_query(req.query):
        funds = _load_funds()
        if req.country:
            funds = [f for f in funds if f["country"] == req.country]
        funds = [f for f in funds if not f.get("is_backup", False)]
        if not funds:
            return ChatResponse(
                answer="I could not find this information in the current source set.",
                is_refusal=False, intent="FUND_LIST", missing_data=True,
            )
        heading = f"## Healthcare Funds — {req.country}" if req.country else "## Available Healthcare Funds"
        rows = "\n".join(f"- {f['fund_name']}" for f in funds)
        return ChatResponse(answer=f"{heading}\n\n{rows}", is_refusal=False, intent="FUND_LIST")

    # Short-circuit: total AUM — use deterministic backend calculation, skip RAG
    if _is_total_aum_query(req.query):
        if not req.country:
            return ChatResponse(
                answer="Please specify a country to calculate total AUM (e.g., 'total AUM for India').",
                is_refusal=False, intent="AGGREGATION",
            )
        all_funds = _load_funds()
        country_funds = [f for f in all_funds if f["country"] == req.country]
        return _country_total_aum(req.country, country_funds)

    # Short-circuit: structured deterministic lookup for factual fund-field questions
    all_funds_for_lookup = _load_funds()
    structured = _structured_lookup(req.query, all_funds_for_lookup)
    if structured is not None:
        return structured

    # 1. Classify
    intent = classify(req.query)

    # 2. Short-circuit on advice / OOS
    if intent in ("ADVICE", "OUT_OF_SCOPE"):
        resp = refusal_response(intent)
        return ChatResponse(
            answer=resp.answer, is_refusal=True, intent=intent,
        )

    # 3. Retrieve
    top_k = 15 if intent == "COMPARISON" else settings.top_k_retrieval
    chunks = retrieve(
        query=req.query,
        country=req.country,
        fund_id=req.fund_id,
        top_k=top_k,
    )

    if not chunks:
        resp = missing_data_response(intent)
        return ChatResponse(
            answer=resp.answer, is_refusal=False, intent=intent, missing_data=True,
        )

    # 4. Rerank
    chunks = rerank(chunks)

    # 5. Confidence gate — require at least 2 directly relevant chunks
    relevant = [c for c in chunks if c.get("rerank_score", 1.0) < CONFIDENCE_THRESHOLD]
    if len(relevant) < 2:
        logger.info(f"Confidence gate triggered: only {len(relevant)} relevant chunk(s) found")
        resp = missing_data_response(intent)
        return ChatResponse(
            answer=resp.answer, is_refusal=False, intent=intent, missing_data=True,
        )

    # 6. Generate — use only the relevant chunks, capped at 8
    max_tokens = 768 if intent == "COMPARISON" else 512
    messages = build_messages(req.query, relevant[:8])
    answer = complete(messages=messages, max_tokens=max_tokens)

    resp = format_response(answer, chunks, intent)

    # Identify the primary fund name from the top relevant chunk (for follow-up context)
    top_fund_name = chunks[0].get("fund_name") if chunks else None

    return ChatResponse(
        answer=resp.answer,
        source_url=resp.source_url,
        platform_url=resp.platform_url,
        last_updated=resp.last_updated,
        fetch_timestamp=resp.fetch_timestamp,
        is_refusal=resp.is_refusal,
        intent=resp.intent,
        missing_data=resp.missing_data,
        fund_name=top_fund_name,
    )


@router.get("/funds/{fund_id}/details", response_model=FundDetails)
async def fund_details(fund_id: str):
    funds = _load_funds()
    match = next((f for f in funds if f["id"] == fund_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Fund not found: {fund_id}")
    slug = _COUNTRY_TO_SLUG.get(match["country"])
    if not slug:
        raise HTTPException(status_code=404, detail=f"No parsed data for country: {match['country']}")
    path = Path("data/parsed") / slug / f"{fund_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No parsed data for fund: {fund_id}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return FundDetails(**data)


@router.get("/funds", response_model=list[FundListItem])
async def list_funds(country: str | None = None):
    funds = _load_funds()
    if country:
        if country not in VALID_COUNTRIES:
            raise HTTPException(status_code=400, detail=f"Unknown country: {country}")
        funds = [f for f in funds if f["country"] == country]
    return [
        FundListItem(
            fund_id=f["id"],
            country=f["country"],
            fund_name=f["fund_name"],
            ticker=f.get("ticker"),
            isin=f.get("isin"),
            fund_type=f["fund_type"],
            domain_subcategory=f["domain_subcategory"],
            currency=f["currency"],
            exchange=f.get("exchange"),
            platform_url=f["platform_url"],
            official_url=f.get("official_url"),
            is_backup=f.get("is_backup", False),
        )
        for f in funds
    ]
