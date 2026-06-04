import re
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from ingestion.logger import get_logger

logger = get_logger("ingestion.html_parser")

MAX_FIELD_CHARS = 2000
MIN_FIELDS_FOR_SUCCESS = 3

# Fields that count toward parse_success
SUCCESS_FIELDS = {
    "expense_ratio", "mer", "ter", "aum", "nav", "benchmark",
    "investment_objective", "risk", "fund_manager", "fund_house",
    "top_holdings", "minimum_investment",
}


@dataclass
class ParsedFund:
    fund_id: str
    country: str
    fund_name: str
    ticker: str | None
    isin: str | None
    source_url: str
    source_type: str
    fetch_timestamp: str
    parse_method: str
    parse_success: bool
    raw_fields: dict[str, str] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    extraction_notes: list[str] = field(default_factory=list)


def _clean(text: str) -> str:
    if not text:
        return ""
    cleaned = " ".join(text.split())
    return cleaned[:MAX_FIELD_CHARS]


def _extract_generic(soup: BeautifulSoup) -> dict[str, str]:
    """
    Generic extraction: scan definition lists, labeled divs, tables,
    and regex fallbacks. Works across ETF.com, TMX, JustETF, Yahoo Finance.
    """
    fields: dict[str, str] = {}

    # --- Strategy 1: <dt>/<dd> definition lists ---
    for dt in soup.find_all("dt"):
        label = _clean(dt.get_text())
        dd = dt.find_next_sibling("dd")
        if dd and label:
            fields[label] = _clean(dd.get_text())

    # --- Strategy 2: labeled div pairs (common in fund pages) ---
    label_patterns = [
        r"expense.ratio|mer|ter|ongoing.charge",
        r"net.assets|aum|fund.size",
        r"nav|net.asset.value|market.price",
        r"benchmark|index.tracked|underlying.index",
        r"risk.rating|riskometer|srri|risk.level",
        r"investment.objective|fund.objective",
        r"fund.manager|portfolio.manager|managed.by",
        r"fund.house|issuer|amc|asset.management",
        r"exit.load|redemption.fee|sales.charge",
        r"minimum.investment|min.sip|min.lumpsum",
        r"distribution|dividend.policy",
        r"exchange|listed.on",
    ]
    combined = "|".join(label_patterns)
    regex = re.compile(combined, re.IGNORECASE)

    for elem in soup.find_all(string=regex):
        label = _clean(elem)
        parent = elem.parent
        # Look for sibling or next element with value
        for sibling in [parent.find_next_sibling(), parent.parent.find_next_sibling()]:
            if sibling:
                val = _clean(sibling.get_text())
                if val and val != label and len(val) > 0:
                    if label not in fields:
                        fields[label] = val
                    break

    # --- Strategy 3: table rows with 2 cells ---
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) == 2:
            label = _clean(cells[0].get_text())
            value = _clean(cells[1].get_text())
            if label and value and label not in fields:
                fields[label] = value

    # --- Strategy 4: regex in raw text ---
    text = soup.get_text(separator=" ", strip=True)
    patterns = {
        "Expense Ratio": r"[Ee]xpense [Rr]atio[:\s]+([0-9]+\.?[0-9]*\s*%)",
        "MER": r"\bMER[:\s]+([0-9]+\.?[0-9]*\s*%)",
        "TER": r"\bTER[:\s]+([0-9]+\.?[0-9]*\s*%)",
        "AUM": r"(?:AUM|Net Assets|Fund Size)[:\s]+([\$\£\€\¥\₹]?[\s]?[0-9,\.]+\s*(?:B|M|Cr|billion|million|crore)?)",
        "NAV": r"\bNAV[:\s]+([\$\£\€\¥\₹]?[\s]?[0-9,\.]+)",
    }
    for label, pat in patterns.items():
        if label not in fields:
            m = re.search(pat, text)
            if m:
                fields[label] = m.group(1).strip()

    # --- Extract holdings from common table structures ---
    holdings = _extract_holdings(soup)
    if holdings:
        fields["Top Holdings"] = holdings

    return fields


def _extract_holdings(soup: BeautifulSoup) -> str:
    """Extract top holdings list as a formatted string."""
    for table in soup.find_all("table"):
        headers = [_clean(th.get_text()).lower() for th in table.find_all("th")]
        if any(h in ["holding", "security", "name", "company"] for h in headers):
            rows = []
            for tr in table.find_all("tr")[1:11]:  # top 10 only
                cells = [_clean(td.get_text()) for td in tr.find_all("td")]
                if len(cells) >= 2 and cells[0] and cells[1]:
                    rows.append(f"{cells[0]} — {cells[1]}")
            if rows:
                return " | ".join(rows)
    return ""


def parse_html(
    fund_id: str,
    country: str,
    fund_name: str,
    ticker: str | None,
    isin: str | None,
    source_url: str,
    source_type: str,
    fetch_timestamp: str,
    html: str,
) -> ParsedFund:
    try:
        soup = BeautifulSoup(html, "lxml")
        # Remove script/style noise
        for tag in soup(["script", "style", "noscript", "nav", "footer"]):
            tag.decompose()

        raw_fields = _extract_generic(soup)
    except Exception as e:
        logger.error(f"{fund_id}: HTML parse exception: {e}")
        raw_fields = {}

    # Count how many success-relevant fields were found
    found_relevant = 0
    for label in raw_fields:
        label_lower = label.lower()
        if any(sf in label_lower.replace(" ", "_") for sf in SUCCESS_FIELDS):
            found_relevant += 1

    notes = []
    if not raw_fields:
        notes.append("No fields extracted — possible JS-rendered or blocked page")

    # Validate fund name match (detect redirect to wrong fund page)
    page_text_lower = html.lower()
    fund_name_fragment = fund_name.split()[0].lower()  # first word of fund name
    if fund_name_fragment not in page_text_lower and len(fund_name_fragment) > 3:
        notes.append(f"Fund name '{fund_name}' not found in page — possible redirect to wrong fund")
        logger.warning(f"{fund_id}: fund name not found in page content — possible redirect")

    return ParsedFund(
        fund_id=fund_id,
        country=country,
        fund_name=fund_name,
        ticker=ticker,
        isin=isin,
        source_url=source_url,
        source_type=source_type,
        fetch_timestamp=fetch_timestamp,
        parse_method="beautifulsoup",
        parse_success=found_relevant >= MIN_FIELDS_FOR_SUCCESS,
        raw_fields=raw_fields,
        missing_fields=[],  # computed by normalizer
        extraction_notes=notes,
    )
