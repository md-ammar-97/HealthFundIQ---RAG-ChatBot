import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from ingestion.html_parser import ParsedFund
from ingestion.logger import get_logger

logger = get_logger("ingestion.normalizer")

_NORM_YAML: dict | None = None

# ── Boilerplate phrases that contaminate many fields ─────────────────────────
_BOILERPLATE = re.compile(
    r"before investing|review the msci|esg fund rating|esg rating|"
    r"download pdf|share email|copy link|share on linkedin|"
    r"intellectual property|morningstar|prospectus|summary prospectus|"
    r"call \d{1,3}-\d{3}|1-866|read it carefully|"
    r"the td logo|trademarks are the property|"
    r"show more|show less|monthly savings rate|compare now|"
    r"savings rate.*€|€.*savings",
    re.IGNORECASE,
)


def _load_normalization() -> dict:
    global _NORM_YAML
    if _NORM_YAML is None:
        path = Path("config/normalization.yaml")
        with open(path, "r", encoding="utf-8") as f:
            _NORM_YAML = yaml.safe_load(f)
    return _NORM_YAML


def _find_value(raw_fields: dict[str, str], variants: list[str]) -> str | None:
    """Case-insensitive partial match against raw field labels."""
    for label, value in raw_fields.items():
        label_lower = label.lower().strip()
        for variant in variants:
            if variant.lower() in label_lower:
                if value and value.strip() not in ("—", "-", "N/A", "n/a", ""):
                    return value.strip()
    return None


# ── Per-field validators / cleaners ──────────────────────────────────────────

def _clean_cost_ratio(v: str | None) -> str | None:
    """Extract a percentage value; discard anything that isn't one."""
    if not v:
        return None
    m = re.search(r"\d+\.?\d*\s*%", v)
    if m:
        cleaned = m.group(0).strip()
        # Sanity-check: realistic expense ratio range 0.01% – 5%
        num = float(re.search(r"[\d.]+", cleaned).group())
        if 0.0 < num < 10:
            return cleaned
    return None


def _clean_nav(v: str | None) -> str | None:
    """Extract first currency+decimal number; strip 52-week range / date cruft."""
    if not v or _BOILERPLATE.search(v):
        return None
    # Must have a currency symbol before the number (bare numbers like "100" are not NAVs)
    m = re.search(r"[₹$€£¥₩]{1,2}\s*[\d,]+\.?\d*", v)
    if m:
        raw_val = m.group(0).strip()
        # Normalise double-dollar ($$164.17 → $164.17)
        raw_val = re.sub(r"^\$+", "$", raw_val)
        return raw_val
    return None


def _clean_aum(v: str | None) -> str | None:
    """Strip trailing date text and validate that a number+unit is present."""
    if not v or _BOILERPLATE.search(v):
        return None
    # Remove "as of/at/on ..." suffixes — may or may not have a leading space
    v = re.sub(r"\s*(as\s+of|as\s+at|as\s+on)\s+.+$", "", v, flags=re.IGNORECASE).strip()
    # Must contain a digit
    if not re.search(r"\d", v):
        return None
    if len(v) < 3:
        return None
    return v


def _clean_benchmark(v: str | None) -> str | None:
    """Must be a real index name — at least 15 chars, not a full prospectus paragraph."""
    if not v or _BOILERPLATE.search(v):
        return None
    v = v.strip()
    if len(v) < 15:
        return None
    # If too long, try to extract just the index name (first sentence or up to first comma)
    if len(v) > 150:
        # Try to pull the first recognisable index name
        m = re.search(
            r"([A-Z][A-Za-z0-9 &®™/\-\.]{10,80}(?:Index|Benchmark|ETF|MSCI|S&P|TOPIX|Hang Seng|Nasdaq|FTSE|Nikkei))",
            v,
        )
        if m:
            return m.group(1).strip()
        # Fall back to first sentence
        first_sentence = v.split(".")[0].strip()
        if 15 <= len(first_sentence) <= 150:
            return first_sentence
        return None  # can't extract a clean name
    return v


def _clean_manager(v: str | None) -> str | None:
    """Manager must be a name — discard percentages, boilerplate, long disclaimers."""
    if not v or _BOILERPLATE.search(v):
        return None
    v = v.strip()
    if len(v) > 150:
        return None
    # Discard if contains a percentage (cost/ratio contamination)
    if "%" in v:
        return None
    # Discard if purely numeric / currency string
    if re.match(r"^[\d$€£¥₹,.\s]+$", v):
        return None
    return v


def _clean_fund_house(v: str | None) -> str | None:
    """Fund house must be a name — discard pure numbers, percentages, boilerplate."""
    if not v or _BOILERPLATE.search(v):
        return None
    v = v.strip()
    if len(v) > 200:
        return None
    # Discard if contains a percentage (cost/ratio contamination)
    if "%" in v:
        return None
    # Discard if purely numeric / currency string
    if re.match(r"^[\d$€£¥₹,.\s]+$", v):
        return None
    return v


def _clean_objective(v: str | None) -> str | None:
    """Investment objective must be a substantive sentence about the fund."""
    if not v or _BOILERPLATE.search(v):
        return None
    v = v.strip()
    if len(v) < 40:
        return None
    # Discard risk-disclaimer or calculator boilerplate
    bad_starts = re.compile(
        r"^(market risk|investment risk|the fund is subject|"
        r"geopolitical|subject to changes in general|"
        r"of the fund is to|monthly savings)",
        re.IGNORECASE,
    )
    if bad_starts.match(v):
        return None
    # Must mention the fund's purpose — contain at least one investing keyword
    if not re.search(
        r"\b(invest|track|replicate|seek|aims to|objective|exposure|"
        r"index|benchmark|return|performance|portfolio)\b",
        v, re.IGNORECASE,
    ):
        return None
    return v[:2000]


def _clean_risk(v: str | None) -> str | None:
    """Risk rating must be short — a label like 'Moderate', '3/7', 'High'."""
    if not v:
        return None
    v = v.strip()
    if len(v) > 50:
        return None
    if _BOILERPLATE.search(v):
        return None
    # Discard if it contains fund share class descriptions
    if re.search(r"\bclass\s+[a-z]\b", v, re.IGNORECASE):
        return None
    # Must match a known risk keyword or numeric rating
    if not re.search(
        r"\b(low|moderate|medium|high|very high|low.moderate|moderate.high|"
        r"\d\s*/\s*\d|srri|risk\s*\d)\b",
        v, re.IGNORECASE,
    ):
        return None
    return v


def _clean_distribution(v: str | None) -> str | None:
    """Extract known distribution policy keyword; discard dates / boilerplate."""
    if not v:
        return None
    _DIST_PATTERNS = re.compile(
        r"\b(monthly|quarterly|semi.annual|annual|annually|"
        r"accumulating|accumulation|distributing|distribution|reinvest)\b",
        re.IGNORECASE,
    )
    m = _DIST_PATTERNS.search(v)
    if m:
        return m.group(0).capitalize()
    return None


def _clean_exit_load(v: str | None) -> str | None:
    """Extract a percentage or 'Nil'; discard garbage."""
    if not v:
        return None
    if re.search(r"\bnil\b", v, re.IGNORECASE):
        return "Nil"
    m = re.search(r"\d+\.?\d*\s*%", v)
    if m:
        return m.group(0).strip()
    return None


def _clean_min_investment(v: str | None) -> str | None:
    """Must contain a currency + number."""
    if not v or _BOILERPLATE.search(v):
        return None
    if not re.search(r"\d", v):
        return None
    if len(v) > 100:
        return None
    return v.strip()


# ── Holdings / exposure parsers ───────────────────────────────────────────────

def _parse_holdings(raw: str | None) -> list[dict] | None:
    if not raw or _BOILERPLATE.search(raw):
        return None
    holdings = []
    for item in re.split(r"\s*[\|,;]\s*", raw):
        parts = re.split(r"\s*—\s*|\s*-\s*(?=[0-9])", item, maxsplit=1)
        if len(parts) == 2:
            name = parts[0].strip()
            weight = parts[1].strip()
            if name and len(name) < 100:
                holdings.append({"name": name, "weight": weight, "ticker": None, "isin": None})
        elif item.strip() and len(item.strip()) < 100:
            holdings.append({"name": item.strip(), "weight": None, "ticker": None, "isin": None})
    return holdings if holdings else None


def _parse_holdings_table(raw: str | None) -> list[dict] | None:
    """
    Parse iShares-style holdings where rows look like:
    'TICKER  COMPANY NAME  WEIGHT%'
    Detects and swaps ticker/name if first token looks like a ticker.
    """
    if not raw or _BOILERPLATE.search(raw):
        return None
    holdings = []
    for item in re.split(r"\s*[\|;]\s*", raw):
        item = item.strip()
        if not item:
            continue
        # Pattern: TICKER — NAME or TICKER NAME WEIGHT
        m = re.match(r"^([A-Z]{1,5})\s+(.+?)\s*$", item)
        if m:
            ticker_candidate = m.group(1)
            rest = m.group(2).strip()
            # Check if rest has a weight at end
            weight_m = re.search(r"(\d+\.?\d*%?)$", rest)
            if weight_m:
                name = rest[: weight_m.start()].strip()
                weight = weight_m.group(1)
            else:
                name = rest
                weight = None
            if name:
                holdings.append({"name": name, "weight": weight, "ticker": ticker_candidate, "isin": None})
        else:
            # Fall back to generic split
            parts = re.split(r"\s*—\s*|\s*-\s*(?=[0-9])", item, maxsplit=1)
            if len(parts) == 2 and len(parts[0]) < 100:
                holdings.append({"name": parts[0].strip(), "weight": parts[1].strip(), "ticker": None, "isin": None})
    return holdings if holdings else None


def _parse_exposure(raw: str | None) -> list[dict] | None:
    if not raw:
        return None
    exposures = []
    for item in re.split(r"\s*[\|,;]\s*", raw):
        m = re.match(r"(.+?)\s*[:\-]\s*([0-9]+\.?[0-9]*\s*%)", item.strip())
        if m:
            exposures.append({"label": m.group(1).strip(), "weight": m.group(2).strip()})
    return exposures if exposures else None


# ── Dataclass ─────────────────────────────────────────────────────────────────

@dataclass
class NormalizedFund:
    fund_id: str
    country_or_market: str
    fund_name: str
    ticker_or_identifier: str | None
    fund_type: str
    domain_subcategory: str
    currency: str
    exchange: str | None
    source_type: str
    platform_url: str
    official_url: str | None
    last_updated_from_source: str | None
    fetch_timestamp: str
    nav_or_price: str | None = None
    aum: str | None = None
    expense_ratio_or_mer_or_ter: str | None = None
    minimum_investment: str | None = None
    minimum_sip: str | None = None
    exit_load_or_redemption_fee: str | None = None
    benchmark: str | None = None
    fund_management: str | None = None
    fund_house_or_issuer: str | None = None
    investment_objective: str | None = None
    risk_rating_or_riskometer: str | None = None
    distribution_policy: str | None = None
    tax_information: str | None = None
    top_10_holdings: list[dict] | None = None
    sector_exposure: list[dict] | None = None
    geographic_exposure: list[dict] | None = None
    documents: list[str] | None = None
    raw_fields: dict[str, str] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    extraction_notes: list[str] = field(default_factory=list)


# ── Main normalize function ───────────────────────────────────────────────────

def normalize(
    parsed: ParsedFund,
    source_metadata: dict,
) -> NormalizedFund:
    norm = _load_normalization()
    country = source_metadata["country"]
    raw = parsed.raw_fields
    c = country

    def pick(norm_key: str) -> str | None:
        variants = norm.get(norm_key, {}).get(c, [])
        return _find_value(raw, variants)

    cost_ratio  = _clean_cost_ratio(pick("cost_ratio"))
    risk        = _clean_risk(pick("risk"))
    fund_size   = _clean_aum(pick("fund_size"))
    price       = _clean_nav(pick("price"))
    exit_cost   = _clean_exit_load(pick("exit_cost"))
    manager     = _clean_manager(pick("fund_manager"))
    house       = _clean_fund_house(pick("fund_house"))
    min_inv     = _clean_min_investment(pick("min_investment"))
    benchmark   = _clean_benchmark(pick("benchmark"))

    # India-specific SIP
    sip = _clean_min_investment(
        _find_value(raw, ["min sip", "minimum sip", "sip amount"])
    ) if country == "India" else None

    # Holdings — try iShares-style table parser first, then generic
    holdings_raw = _find_value(raw, ["top holdings", "top 10 holdings", "holdings"])
    holdings = _parse_holdings_table(holdings_raw) or _parse_holdings(holdings_raw)

    sector_raw = _find_value(raw, ["sector", "sector allocation", "sector exposure"])
    sector = _parse_exposure(sector_raw)

    geo_raw = _find_value(raw, ["geographic", "country allocation", "geographic exposure"])
    geo = _parse_exposure(geo_raw)

    objective = _clean_objective(
        _find_value(raw, ["investment objective", "fund objective", "objective"])
    )

    dist = _clean_distribution(
        _find_value(raw, ["distribution", "dividend policy", "accumulating", "distributing"])
    )

    # Last updated — look for date in raw values
    last_updated = None
    date_pattern = re.compile(
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b"
        r"|\b\d{4}-\d{2}-\d{2}\b",
        re.IGNORECASE,
    )
    for val in raw.values():
        m = date_pattern.search(val)
        if m:
            last_updated = m.group(0)
            break

    all_norm_fields = [
        "nav_or_price", "aum", "expense_ratio_or_mer_or_ter",
        "minimum_investment", "benchmark", "fund_management",
        "fund_house_or_issuer", "investment_objective", "risk_rating_or_riskometer",
        "top_10_holdings", "sector_exposure", "distribution_policy",
    ]
    values_map = {
        "nav_or_price": price, "aum": fund_size,
        "expense_ratio_or_mer_or_ter": cost_ratio, "minimum_investment": min_inv,
        "benchmark": benchmark, "fund_management": manager,
        "fund_house_or_issuer": house, "investment_objective": objective,
        "risk_rating_or_riskometer": risk, "top_10_holdings": holdings,
        "sector_exposure": sector, "distribution_policy": dist,
    }
    missing = [f for f in all_norm_fields if not values_map.get(f)]

    result = NormalizedFund(
        fund_id=parsed.fund_id,
        country_or_market=country,
        fund_name=parsed.fund_name,
        ticker_or_identifier=parsed.ticker or source_metadata.get("isin"),
        fund_type=source_metadata["fund_type"],
        domain_subcategory=source_metadata["domain_subcategory"],
        currency=source_metadata["currency"],
        exchange=source_metadata.get("exchange"),
        source_type=parsed.source_type,
        platform_url=source_metadata["platform_url"],
        official_url=source_metadata.get("official_url"),
        last_updated_from_source=last_updated,
        fetch_timestamp=parsed.fetch_timestamp,
        nav_or_price=price,
        aum=fund_size,
        expense_ratio_or_mer_or_ter=cost_ratio,
        minimum_investment=min_inv,
        minimum_sip=sip,
        exit_load_or_redemption_fee=exit_cost,
        benchmark=benchmark,
        fund_management=manager,
        fund_house_or_issuer=house,
        investment_objective=objective,
        risk_rating_or_riskometer=risk,
        distribution_policy=dist,
        top_10_holdings=holdings,
        sector_exposure=sector,
        geographic_exposure=geo,
        raw_fields=raw,
        missing_fields=missing,
        extraction_notes=parsed.extraction_notes,
    )

    logger.info(f"{parsed.fund_id}: normalized | missing={missing}")
    return result


def merge_normalized(official: NormalizedFund | None, platform: NormalizedFund | None) -> NormalizedFund:
    """
    Merge two NormalizedFund objects for the same fund.
    Official source values take precedence. Platform fills gaps.
    """
    if official is None:
        return platform
    if platform is None:
        return official

    for field_name in [
        "nav_or_price", "aum", "expense_ratio_or_mer_or_ter",
        "minimum_investment", "minimum_sip", "exit_load_or_redemption_fee",
        "benchmark", "fund_management", "fund_house_or_issuer",
        "investment_objective", "risk_rating_or_riskometer",
        "distribution_policy", "top_10_holdings", "sector_exposure",
        "geographic_exposure", "last_updated_from_source", "documents",
    ]:
        official_val = getattr(official, field_name)
        platform_val = getattr(platform, field_name)
        if not official_val and platform_val:
            setattr(official, field_name, platform_val)

    for k, v in platform.raw_fields.items():
        if k not in official.raw_fields:
            official.raw_fields[k] = v

    official.extraction_notes = list(set(official.extraction_notes + platform.extraction_notes))

    all_fields = [
        "nav_or_price", "aum", "expense_ratio_or_mer_or_ter",
        "minimum_investment", "benchmark", "fund_management",
        "fund_house_or_issuer", "investment_objective", "risk_rating_or_riskometer",
        "top_10_holdings", "sector_exposure", "distribution_policy",
    ]
    official.missing_fields = [f for f in all_fields if not getattr(official, f)]

    return official
