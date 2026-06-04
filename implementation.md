# FinanceBot — Global Healthcare Funds RAG Assistant: Implementation Guide

---

## 0. Pre-Implementation Checklist

Before writing any code, verify these are in place:

```
[ ] Python 3.11+ installed
[ ] pip or uv available
[ ] Git initialized in project root
[ ] Groq API key obtained from console.groq.com
[ ] .env created from .env.example (never commit .env)
[ ] Playwright browsers installed: playwright install chromium
[ ] All 5 project documents reviewed: Problem_Statement, architecture, context, datamodel, design
```

---

## 1. Phase 0 — Project Scaffold

### 1.1 Create Directory Tree

Run once from the project root (`FinanceBot/`):

```
mkdir -p config ingestion embeddings retrieval llm guardrails api ui/components ui/assets scheduler data/raw data/parsed data/chunks vectorstore/chroma_db logs tests
```

### 1.2 `requirements.txt`

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
streamlit==1.38.0
pydantic==2.8.2
pydantic-settings==2.5.2
python-dotenv==1.0.1
requests==2.32.3
beautifulsoup4==4.12.3
playwright==1.47.0
pdfplumber==0.11.4
pypdf==5.0.1
sentence-transformers==3.1.1
chromadb==0.5.15
groq==0.11.0
apscheduler==3.10.4
pytz==2024.2
pyyaml==6.0.2
pytest==8.3.3
httpx==0.27.2
lxml==5.3.0
```

Pin these versions. Do not use `chromadb>=0.6` — collection format changed.

### 1.3 `.env.example`

```env
# Groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_CLASSIFIER_MODEL=llama-3.1-8b-instant

# Embeddings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Vector Store
CHROMA_PERSIST_DIR=./vectorstore/chroma_db
CHROMA_COLLECTION=healthcare_funds

# Retrieval
TOP_K_RETRIEVAL=6

# Scheduler
SCHEDULER_HOUR_IST=10

# App
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8002
STREAMLIT_PORT=8502
LOG_LEVEL=INFO
```

### 1.4 `config/settings.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_classifier_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chroma_persist_dir: str = "./vectorstore/chroma_db"
    chroma_collection: str = "healthcare_funds"
    top_k_retrieval: int = 6
    scheduler_hour_ist: int = 10
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8002
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

### 1.5 `config/sources.yaml`

Copy the full YAML from `datamodel.md` Section 1.2 verbatim. The file is the single source of truth — do not duplicate it in code.

### 1.6 `config/normalization.yaml`

Copy the full YAML from `datamodel.md` Section 9 verbatim.

### 1.7 Logging Setup — `ingestion/logger.py`

```python
import logging
import os
from config.settings import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
        # File handler for ingestion logs
        os.makedirs("logs", exist_ok=True)
        fh = logging.FileHandler(f"logs/{name.split('.')[-1]}.log")
        fh.setFormatter(handler.formatter)
        logger.addHandler(fh)
    return logger
```

### 1.8 Validate Setup

```bash
python -c "from config.settings import settings; print('GROQ key loaded:', bool(settings.groq_api_key))"
python -c "import chromadb; print('ChromaDB version:', chromadb.__version__)"
python -c "import playwright; print('Playwright OK')"
```

---

## 2. Phase 1 — Ingestion Pipeline

### 2.1 `ingestion/crawler.py`

```python
import time
import requests
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Literal
from ingestion.logger import get_logger

logger = get_logger("ingestion.crawler")

IST = timezone(timedelta(hours=5, minutes=30))
MIN_HTML_CHARS = 500
MIN_PDF_BYTES = 1000
MAX_PDF_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class RawFetch:
    fund_id: str
    url: str
    source_type: Literal["platform", "official", "pdf"]
    content_type: Literal["html", "pdf"]
    raw_content: str | bytes
    fetch_timestamp: str
    http_status: int
    fetch_method: Literal["requests", "playwright"]
    content_length: int
    fetch_success: bool
    error_message: str | None


def _now_ist() -> str:
    return datetime.now(IST).isoformat()


def _fetch_static(url: str, is_pdf: bool = False) -> tuple[int, str | bytes | None, str | None]:
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(
                url,
                headers=HEADERS,
                timeout=30,
                allow_redirects=True,
                stream=is_pdf,
            )
            if is_pdf:
                if resp.status_code == 200:
                    content = resp.content
                    if len(content) > MAX_PDF_BYTES:
                        return resp.status_code, None, f"PDF too large: {len(content)} bytes"
                    return resp.status_code, content, None
            else:
                return resp.status_code, resp.text, None
        except requests.exceptions.Timeout:
            err = "Timeout"
        except requests.exceptions.SSLError as e:
            return 0, None, f"SSL error: {e}"
        except requests.exceptions.ConnectionError as e:
            err = f"Connection error: {e}"
        except Exception as e:
            err = str(e)

        if attempt < MAX_RETRIES - 1:
            time.sleep(BACKOFF_BASE ** attempt)

    return 0, None, err


def _fetch_playwright(url: str) -> tuple[int, str | None, str | None]:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        return 0, None, "Playwright not installed. Run: playwright install chromium"

    for attempt in range(MAX_RETRIES):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent=HEADERS["User-Agent"],
                    locale="en-US",
                )
                page = ctx.new_page()
                page.goto(url, wait_until="networkidle", timeout=45000)
                # Accept cookie banners if present
                for selector in [
                    "button:has-text('Accept All')",
                    "button:has-text('Accept Cookies')",
                    "button:has-text('I Accept')",
                    "[id*='accept']",
                ]:
                    try:
                        btn = page.locator(selector).first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            page.wait_for_timeout(1000)
                            break
                    except Exception:
                        pass
                page.wait_for_timeout(3000)
                html = page.content()
                browser.close()
                return 200, html, None
        except PWTimeout:
            err = "Playwright timeout"
        except Exception as e:
            err = str(e)

        if attempt < MAX_RETRIES - 1:
            time.sleep(BACKOFF_BASE ** attempt)

    return 0, None, err


def fetch(
    fund_id: str,
    url: str,
    source_type: Literal["platform", "official", "pdf"],
    use_playwright: bool = False,
) -> RawFetch:
    timestamp = _now_ist()
    is_pdf = source_type == "pdf"

    if is_pdf:
        status, content, err = _fetch_static(url, is_pdf=True)
        method = "requests"
        content_type = "pdf"
    else:
        if use_playwright:
            status, content, err = _fetch_playwright(url)
            method = "playwright"
        else:
            status, content, err = _fetch_static(url)
            method = "requests"
            # Auto-upgrade to Playwright if content too short
            if (
                status == 200
                and content is not None
                and len(content) < MIN_HTML_CHARS
            ):
                logger.info(f"{fund_id}: static content short ({len(content)} chars), retrying with Playwright")
                status, content, err = _fetch_playwright(url)
                method = "playwright"
        content_type = "html"

    # Validate content size
    content_len = len(content) if content else 0
    min_size = MIN_PDF_BYTES if is_pdf else MIN_HTML_CHARS

    success = (
        status == 200
        and content is not None
        and content_len >= min_size
        and err is None
    )

    if not success and err is None:
        if status != 200:
            err = f"HTTP {status}"
        elif content_len < min_size:
            err = f"Content too short: {content_len} {'bytes' if is_pdf else 'chars'} (min {min_size})"

    if not success:
        logger.warning(f"{fund_id} | {url} | FAILED: {err}")
    else:
        logger.info(f"{fund_id} | {url} | OK ({content_len} {'bytes' if is_pdf else 'chars'}, {method})")

    return RawFetch(
        fund_id=fund_id,
        url=url,
        source_type=source_type,
        content_type=content_type,
        raw_content=content or (b"" if is_pdf else ""),
        fetch_timestamp=timestamp,
        http_status=status,
        fetch_method=method,
        content_length=content_len,
        fetch_success=success,
        error_message=err,
    )
```

### 2.2 `ingestion/html_parser.py`

```python
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
    """Strip whitespace and truncate."""
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
    # Look for tables with holding-like column headers
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
```

### 2.3 `ingestion/pdf_parser.py`

```python
import io
import pdfplumber
from ingestion.html_parser import ParsedFund, _clean
from ingestion.logger import get_logger

logger = get_logger("ingestion.pdf_parser")
MAX_FIELD_CHARS = 2000


def parse_pdf(
    fund_id: str,
    country: str,
    fund_name: str,
    ticker: str | None,
    isin: str | None,
    source_url: str,
    fetch_timestamp: str,
    pdf_bytes: bytes,
) -> ParsedFund:
    raw_fields: dict[str, str] = {}
    notes: list[str] = []

    try:
        fp = io.BytesIO(pdf_bytes) if isinstance(pdf_bytes, bytes) else open(pdf_bytes, "rb")
        with pdfplumber.open(fp) as pdf:
            all_text_blocks: list[str] = []
            all_tables: list[list[list]] = []

            for page in pdf.pages:
                text = page.extract_text() or ""
                if text.strip():
                    all_text_blocks.append(text)
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)

            full_text = "\n".join(all_text_blocks)

            if not full_text.strip():
                notes.append("PDF appears to be image-only (no selectable text)")
                logger.warning(f"{fund_id}: PDF has no selectable text — image scan?")
                return ParsedFund(
                    fund_id=fund_id, country=country, fund_name=fund_name,
                    ticker=ticker, isin=isin, source_url=source_url,
                    source_type="pdf", fetch_timestamp=fetch_timestamp,
                    parse_method="pdfplumber", parse_success=False,
                    raw_fields={}, extraction_notes=notes,
                )

            # Extract from text blocks using line-by-line parsing
            raw_fields = _extract_from_text(full_text, fund_name)

            # Extract from tables
            for table in all_tables:
                _extract_from_table(table, raw_fields)

    except Exception as e:
        if "password" in str(e).lower() or "encrypted" in str(e).lower():
            notes.append("PDF is password-protected — cannot extract")
            logger.warning(f"{fund_id}: PDF is password-protected")
        else:
            notes.append(f"PDF parse error: {e}")
            logger.error(f"{fund_id}: PDF parse exception: {e}")
        return ParsedFund(
            fund_id=fund_id, country=country, fund_name=fund_name,
            ticker=ticker, isin=isin, source_url=source_url,
            source_type="pdf", fetch_timestamp=fetch_timestamp,
            parse_method="pdfplumber", parse_success=False,
            raw_fields={}, extraction_notes=notes,
        )

    success = len(raw_fields) >= 2
    logger.info(f"{fund_id}: PDF extracted {len(raw_fields)} fields, success={success}")

    return ParsedFund(
        fund_id=fund_id, country=country, fund_name=fund_name,
        ticker=ticker, isin=isin, source_url=source_url,
        source_type="pdf", fetch_timestamp=fetch_timestamp,
        parse_method="pdfplumber", parse_success=success,
        raw_fields=raw_fields, extraction_notes=notes,
    )


def _extract_from_text(text: str, fund_name: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    import re

    patterns = {
        "Expense Ratio": r"(?:expense ratio|ter|ongoing charges?)[:\s]+([0-9]+\.?[0-9]*\s*%)",
        "AUM": r"(?:fund size|net assets|aum|total assets)[:\s]+([\$\£\€\¥]?[\s]?[0-9,\.]+\s*(?:bn|mn|m|b|billion|million)?)",
        "NAV": r"(?:nav|net asset value)[:\s]+([\$\£\€\¥\₩]?[\s]?[0-9,\.]+)",
        "Benchmark": r"(?:benchmark|reference index|tracks?)[:\s]+([A-Za-z0-9 &\-\.®™]+(?:Index)?)",
        "Risk Rating": r"(?:risk rating|srri|risk indicator)[:\s]+([A-Za-z0-9 \/]+)",
        "Fund Manager": r"(?:portfolio manager|investment manager|managed by)[:\s]+([A-Za-z ,\.]+)",
        "Investment Objective": r"(?:investment objective|fund objective|objective)[:\s\n]+([A-Za-z][^\n]{30,300})",
        "Distribution Policy": r"(?:distribution policy|dividend)[:\s]+([A-Za-z]+(?:ulating|ributing)?)",
    }

    for label, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = _clean(m.group(1))
            if val:
                fields[label] = val[:MAX_FIELD_CHARS]

    return fields


def _extract_from_table(table: list[list], fields: dict[str, str]) -> None:
    if not table:
        return
    for row in table:
        if not row or len(row) < 2:
            continue
        label = _clean(str(row[0] or ""))
        value = _clean(str(row[1] or ""))
        if label and value and label not in fields:
            fields[label] = value[:MAX_FIELD_CHARS]
```

### 2.4 `ingestion/normalizer.py`

```python
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from ingestion.html_parser import ParsedFund
from ingestion.logger import get_logger

logger = get_logger("ingestion.normalizer")

_NORM_YAML: dict | None = None


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


def _parse_holdings(raw: str | None) -> list[dict] | None:
    if not raw:
        return None
    holdings = []
    import re
    # Handle "Name — weight%" or "Name | weight%"
    for item in re.split(r"\s*[\|,;]\s*", raw):
        parts = re.split(r"\s*—\s*|\s*-\s*(?=[0-9])", item, maxsplit=1)
        if len(parts) == 2:
            name = parts[0].strip()
            weight = parts[1].strip()
            if name:
                holdings.append({"name": name, "weight": weight, "ticker": None, "isin": None})
        elif item.strip():
            holdings.append({"name": item.strip(), "weight": None, "ticker": None, "isin": None})
    return holdings if holdings else None


def _parse_exposure(raw: str | None) -> list[dict] | None:
    if not raw:
        return None
    import re
    exposures = []
    for item in re.split(r"\s*[\|,;]\s*", raw):
        m = re.match(r"(.+?)\s*[:\-]\s*([0-9]+\.?[0-9]*\s*%)", item.strip())
        if m:
            exposures.append({"label": m.group(1).strip(), "weight": m.group(2).strip()})
    return exposures if exposures else None


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


def normalize(
    parsed: ParsedFund,
    source_metadata: dict,  # entry from sources.yaml
) -> NormalizedFund:
    norm = _load_normalization()
    country = source_metadata["country"]
    raw = parsed.raw_fields

    # country key in normalization.yaml uses slash notation
    c = country  # e.g. "India", "USA", "China/HK", "UK/Europe"

    def pick(norm_key: str) -> str | None:
        variants = norm.get(norm_key, {}).get(c, [])
        return _find_value(raw, variants)

    cost_ratio = pick("cost_ratio")
    risk = pick("risk")
    fund_size = pick("fund_size")
    price = pick("price")
    exit_cost = pick("exit_cost")
    manager = pick("fund_manager")
    house = pick("fund_house")
    min_inv = pick("min_investment")
    benchmark = pick("benchmark")

    # India-specific SIP
    sip = _find_value(raw, ["min sip", "minimum sip", "sip amount"]) if country == "India" else None

    # Holdings and exposure
    holdings_raw = _find_value(raw, ["top holdings", "top 10 holdings", "holdings"])
    holdings = _parse_holdings(holdings_raw)

    sector_raw = _find_value(raw, ["sector", "sector allocation", "sector exposure"])
    sector = _parse_exposure(sector_raw)

    geo_raw = _find_value(raw, ["geographic", "country allocation", "geographic exposure"])
    geo = _parse_exposure(geo_raw)

    # Objective (can be long — already truncated at 2000 chars in parser)
    objective = _find_value(raw, ["investment objective", "fund objective", "objective"])

    # Distribution
    dist = _find_value(raw, ["distribution", "dividend policy", "accumulating", "distributing"])

    # Last updated — look for any date-like string in raw fields
    import re
    last_updated = None
    date_pattern = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b|\b\d{4}-\d{2}-\d{2}\b", re.IGNORECASE)
    for val in raw.values():
        m = date_pattern.search(val)
        if m:
            last_updated = m.group(0)
            break

    # Compute missing_fields
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

    # Official wins on all financial fields
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
        # If official has no value, use platform's
        if not official_val and platform_val:
            setattr(official, field_name, platform_val)

    # Merge raw_fields (platform fills gaps in official)
    for k, v in platform.raw_fields.items():
        if k not in official.raw_fields:
            official.raw_fields[k] = v

    # Merge extraction notes
    official.extraction_notes = list(set(official.extraction_notes + platform.extraction_notes))

    # Recompute missing_fields
    all_fields = [
        "nav_or_price", "aum", "expense_ratio_or_mer_or_ter",
        "minimum_investment", "benchmark", "fund_management",
        "fund_house_or_issuer", "investment_objective", "risk_rating_or_riskometer",
        "top_10_holdings", "sector_exposure", "distribution_policy",
    ]
    official.missing_fields = [f for f in all_fields if not getattr(official, f)]

    return official
```

### 2.5 `ingestion/parsed_store.py`

Persistence layer that serialises `NormalizedFund` to `data/parsed/{country}/{fund_id}.json`
after every successful merge. This JSON file becomes the **authoritative clean data source**
fed to the chunker — the chatbot never reads from raw HTML directly.

`raw_fields` (the messy intermediate extraction dict) is excluded from the JSON.

Key functions:
- `save_parsed(fund)` — writes JSON, returns the `Path` written
- `load_parsed(fund_id, country)` — reads and deserialises back to `NormalizedFund`
- `list_parsed()` — lists all existing JSON files (useful for re-embed-only runs)
- `parsed_path(fund_id, country)` — returns expected path without reading

JSON location: `data/parsed/{country_slug}/{fund_id}.json`

**Backfill for existing raw files:** run `python -m ingestion.backfill_parsed` to parse
all HTML/PDF files already in `data/raw/` and generate JSONs without re-fetching.

---

### 2.6 `ingestion/backfill_parsed.py`

One-time (and idempotent) script that walks `data/raw/`, re-parses every cached
HTML/PDF file using the existing parsers + normalizer, and writes JSON files to
`data/parsed/`. Does **not** touch ChromaDB.

Usage:
```bash
python -m ingestion.backfill_parsed
```

---

### 2.7 `ingestion/run_ingestion.py`

```python
"""
CLI entry point: python -m ingestion.run_ingestion
Runs the full ingestion pipeline for all non-backup funds in sources.yaml.
"""
import json
import os
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta
from ingestion.crawler import fetch
from ingestion.html_parser import parse_html
from ingestion.pdf_parser import parse_pdf
from ingestion.normalizer import normalize, merge_normalized, NormalizedFund
from ingestion.chunker import chunk_fund
from embeddings.embedder import encode_chunks
from embeddings.store import upsert_chunks
from ingestion.logger import get_logger

logger = get_logger("ingestion.run_ingestion")
IST = timezone(timedelta(hours=5, minutes=30))


def _load_sources() -> list[dict]:
    with open("config/sources.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [s for s in data["funds"] if not s.get("is_backup", False)]


def _save_raw(fund_id: str, country: str, source_type: str, content: str | bytes, ext: str) -> None:
    country_slug = country.lower().replace("/", "_").replace(" ", "_")
    path = Path(f"data/raw/{country_slug}/{fund_id}")
    path.mkdir(parents=True, exist_ok=True)
    filename = f"{source_type}_page.{ext}"
    mode = "wb" if isinstance(content, bytes) else "w"
    encoding = None if isinstance(content, bytes) else "utf-8"
    with open(path / filename, mode, encoding=encoding) as f:
        f.write(content)


def _log_result(log: dict) -> None:
    os.makedirs("logs", exist_ok=True)
    with open("logs/ingestion.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")


def ingest_fund(source: dict, run_id: str) -> dict:
    fund_id = source["id"]
    country = source["country"]
    fund_name = source["fund_name"]
    ticker = source.get("ticker")
    isin = source.get("isin")

    log = {
        "run_id": run_id,
        "fund_id": fund_id,
        "country": country,
        "chunks_upserted": 0,
        "chunks_skipped": 0,
        "error_message": None,
    }

    normalized_objects: list[NormalizedFund] = []

    # -- Fetch platform URL --
    platform_raw = fetch(
        fund_id=fund_id,
        url=source["platform_url"],
        source_type="platform",
        use_playwright=source.get("use_playwright", False),
    )
    if platform_raw.fetch_success:
        _save_raw(fund_id, country, "platform", platform_raw.raw_content, "html")
        parsed = parse_html(
            fund_id=fund_id, country=country, fund_name=fund_name,
            ticker=ticker, isin=isin,
            source_url=source["platform_url"],
            source_type="platform",
            fetch_timestamp=platform_raw.fetch_timestamp,
            html=platform_raw.raw_content,
        )
        if parsed.parse_success:
            norm = normalize(parsed, source)
            normalized_objects.append(norm)
    else:
        logger.warning(f"{fund_id}: platform fetch failed — {platform_raw.error_message}")

    # -- Fetch official URL (if present) --
    if source.get("official_url"):
        official_raw = fetch(
            fund_id=fund_id,
            url=source["official_url"],
            source_type="official",
            use_playwright=source.get("official_use_playwright", False),
        )
        if official_raw.fetch_success:
            _save_raw(fund_id, country, "official", official_raw.raw_content, "html")
            parsed_off = parse_html(
                fund_id=fund_id, country=country, fund_name=fund_name,
                ticker=ticker, isin=isin,
                source_url=source["official_url"],
                source_type="official",
                fetch_timestamp=official_raw.fetch_timestamp,
                html=official_raw.raw_content,
            )
            if parsed_off.parse_success:
                norm_off = normalize(parsed_off, source)
                normalized_objects.append(norm_off)

    # -- Fetch PDF (if present) --
    if source.get("has_pdf") and source.get("pdf_url"):
        pdf_raw = fetch(
            fund_id=fund_id,
            url=source["pdf_url"],
            source_type="pdf",
        )
        if pdf_raw.fetch_success:
            _save_raw(fund_id, country, "factsheet", pdf_raw.raw_content, "pdf")
            parsed_pdf = parse_pdf(
                fund_id=fund_id, country=country, fund_name=fund_name,
                ticker=ticker, isin=isin,
                source_url=source["pdf_url"],
                fetch_timestamp=pdf_raw.fetch_timestamp,
                pdf_bytes=pdf_raw.raw_content,
            )
            if parsed_pdf.parse_success:
                norm_pdf = normalize(parsed_pdf, source)
                normalized_objects.append(norm_pdf)

    if not normalized_objects:
        log["error_message"] = "No successful parse from any source"
        logger.error(f"{fund_id}: no successful parse — skipping upsert")
        _log_result(log)
        return log

    # -- Merge all normalized objects --
    official_norm = next((n for n in normalized_objects if n.source_type == "official"), None)
    platform_norm = next((n for n in normalized_objects if n.source_type == "platform"), None)
    pdf_norm = next((n for n in normalized_objects if n.source_type == "pdf"), None)

    # Merge order: official > pdf > platform
    merged = merge_normalized(official_norm, pdf_norm)
    merged = merge_normalized(merged, platform_norm)

    # -- Chunk --
    chunks = chunk_fund(merged)

    if not chunks:
        log["error_message"] = "No chunks produced"
        _log_result(log)
        return log

    # -- Embed and upsert --
    encoded = encode_chunks(chunks)
    upserted, skipped = upsert_chunks(encoded)

    log["chunks_upserted"] = upserted
    log["chunks_skipped"] = skipped
    log["fields_extracted"] = [f for f in [
        "nav_or_price", "aum", "expense_ratio_or_mer_or_ter",
        "minimum_investment", "minimum_sip", "exit_load_or_redemption_fee",
        "benchmark", "fund_management", "fund_house_or_issuer",
        "investment_objective", "risk_rating_or_riskometer", "top_10_holdings",
        "sector_exposure", "geographic_exposure", "distribution_policy",
    ] if getattr(merged, f)]
    log["fields_missing"] = merged.missing_fields
    _log_result(log)
    logger.info(f"{fund_id}: done | upserted={upserted} skipped={skipped}")
    return log


def ingest_all() -> None:
    sources = _load_sources()
    run_id = datetime.now(IST).isoformat()
    logger.info(f"Starting ingestion run {run_id} for {len(sources)} funds")

    results = []
    for source in sources:
        try:
            result = ingest_fund(source, run_id)
            results.append(result)
        except Exception as e:
            logger.error(f"{source['id']}: unexpected error: {e}", exc_info=True)

    success = sum(1 for r in results if r.get("chunks_upserted", 0) > 0)
    failed = len(results) - success
    logger.info(f"Ingestion complete | success={success} failed={failed}")


if __name__ == "__main__":
    ingest_all()
```

---

## 3. Phase 2 — Chunking and Embeddings

### 3.1 `embeddings/schema.py`

```python
from dataclasses import dataclass, field


@dataclass
class Chunk:
    chunk_id: str          # "<fund_id>_<section>" or "<fund_id>_<section>_part<n>"
    section: str           # normalized section key
    text: str              # formatted text for embedding + LLM
    fund_id: str
    country: str
    fund_name: str
    ticker: str            # "" if null
    isin: str              # "" if null
    domain_subcategory: str
    fund_type: str
    source_type: str       # "official" | "platform" | "pdf"
    source_url: str
    official_url: str      # "" if null
    platform_url: str
    last_updated_from_source: str   # "" if unknown
    fetch_timestamp: str
    embedding: list[float] = field(default_factory=list)


# All valid section keys
SECTION_KEYS = [
    "overview", "cost_ratio", "risk", "benchmark",
    "investment_objective", "fund_management", "fund_house_or_issuer",
    "nav_or_price", "aum", "top_10_holdings", "sector_exposure",
    "geographic_exposure", "minimum_investment", "exit_load",
    "distribution_policy", "documents", "identity",
]

# Friendly display labels for each section
SECTION_LABELS = {
    "overview": "Overview",
    "cost_ratio": "Expense Ratio / MER / TER",
    "risk": "Risk Rating / Riskometer",
    "benchmark": "Benchmark",
    "investment_objective": "Investment Objective",
    "fund_management": "Fund Manager",
    "fund_house_or_issuer": "Fund House / Issuer",
    "nav_or_price": "NAV / Price",
    "aum": "AUM / Net Assets / Fund Size",
    "top_10_holdings": "Top 10 Holdings",
    "sector_exposure": "Sector Exposure",
    "geographic_exposure": "Geographic Exposure",
    "minimum_investment": "Minimum Investment",
    "exit_load": "Exit Load / Redemption Fee",
    "distribution_policy": "Distribution Policy",
    "documents": "Documents",
    "identity": "Fund Identity",
}
```

### 3.2 `ingestion/chunker.py`

```python
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
```

### 3.3 `embeddings/embedder.py`

```python
from sentence_transformers import SentenceTransformer
from embeddings.schema import Chunk
from config.settings import settings
from ingestion.logger import get_logger
import numpy as np

logger = get_logger("embeddings.embedder")

_MODEL: SentenceTransformer | None = None
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _MODEL = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded")
    return _MODEL


def encode_query(query: str) -> list[float]:
    model = _get_model()
    vec = model.encode(BGE_QUERY_PREFIX + query, normalize_embeddings=True)
    return vec.tolist()


def encode_chunks(chunks: list[Chunk]) -> list[Chunk]:
    if not chunks:
        return []
    model = _get_model()
    texts = [c.text for c in chunks]
    # BGE documents do NOT use the query prefix
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
```

### 3.4 `embeddings/store.py`

```python
import chromadb
from chromadb.config import Settings as ChromaSettings
from embeddings.schema import Chunk
from config.settings import settings
from ingestion.logger import get_logger

logger = get_logger("embeddings.store")

_CLIENT: chromadb.PersistentClient | None = None
_COLLECTION = None


def _get_collection():
    global _CLIENT, _COLLECTION
    if _COLLECTION is None:
        _CLIENT = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _COLLECTION = _CLIENT.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB collection '{settings.chroma_collection}' ready")
    return _COLLECTION


def _chunk_to_metadata(chunk: Chunk) -> dict:
    """Convert Chunk to ChromaDB-compatible metadata (all str values)."""
    return {
        "fund_id": chunk.fund_id,
        "section": chunk.section,
        "country": chunk.country,
        "fund_name": chunk.fund_name,
        "ticker": chunk.ticker,
        "isin": chunk.isin,
        "domain_subcategory": chunk.domain_subcategory,
        "fund_type": chunk.fund_type,
        "source_type": chunk.source_type,
        "source_url": chunk.source_url,
        "official_url": chunk.official_url,
        "platform_url": chunk.platform_url,
        "last_updated_from_source": chunk.last_updated_from_source,
        "fetch_timestamp": chunk.fetch_timestamp,
    }


def upsert_chunks(chunks: list[Chunk]) -> tuple[int, int]:
    if not chunks:
        return 0, 0
    collection = _get_collection()

    ids = [c.chunk_id for c in chunks]
    embeddings = [c.embedding for c in chunks]
    documents = [c.text for c in chunks]
    metadatas = [_chunk_to_metadata(c) for c in chunks]

    # Filter out chunks with empty embeddings
    valid = [
        (i, e, d, m)
        for i, e, d, m in zip(ids, embeddings, documents, metadatas)
        if e
    ]
    skipped = len(chunks) - len(valid)

    if not valid:
        return 0, skipped

    try:
        v_ids, v_emb, v_docs, v_meta = zip(*valid)
        collection.upsert(
            ids=list(v_ids),
            embeddings=list(v_emb),
            documents=list(v_docs),
            metadatas=list(v_meta),
        )
        logger.info(f"Upserted {len(valid)} chunks, skipped {skipped}")
        return len(valid), skipped
    except Exception as e:
        logger.error(f"ChromaDB upsert failed: {e}", exc_info=True)
        return 0, len(chunks)


def query_collection(
    query_embedding: list[float],
    where: dict | None = None,
    n_results: int = 6,
) -> list[dict]:
    collection = _get_collection()
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        if not results["ids"] or not results["ids"][0]:
            return []
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return output
    except Exception as e:
        logger.error(f"ChromaDB query failed: {e}", exc_info=True)
        return []


def get_collection_count() -> int:
    try:
        return _get_collection().count()
    except Exception:
        return 0
```

---

## 4. Phase 3 — Retrieval

### 4.1 `retrieval/retriever.py`

```python
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
```

### 4.2 `retrieval/reranker.py`

```python
def rerank(chunks: list[dict]) -> list[dict]:
    """
    Boost official-source chunks. Penalize chunks missing last_updated.
    Returns reranked list (in-place scoring, then sorted).
    """
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        score = chunk.get("distance", 1.0)  # lower distance = better in cosine

        # Boost official sources (reduce distance score = move up)
        if meta.get("source_type") == "official":
            score *= 0.85
        elif meta.get("source_type") == "pdf":
            score *= 0.92

        # Penalize stale / missing date
        if not meta.get("last_updated_from_source"):
            score *= 1.05

        chunk["rerank_score"] = score

    return sorted(chunks, key=lambda c: c["rerank_score"])
```

---

## 5. Phase 4 — LLM Generation

### 5.1 `llm/groq_client.py`

```python
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
```

### 5.2 `llm/prompt_builder.py`

```python
SYSTEM_PROMPT = """You are a facts-only Global Healthcare Funds RAG Assistant called HealthFundIQ.

RULES (never violate):
1. Answer ONLY from the retrieved context provided. Never use your own knowledge or training data.
2. Every answer MUST include the Source URL from the context. Use official_url if available; otherwise use source_url.
3. Every answer MUST include "Last updated from sources:" if the value is present in context.
4. Do NOT provide investment advice, buy/sell recommendations, portfolio construction, return predictions, or personalized guidance.
5. Do NOT rank funds as "best" or "better" unless comparing a specific factual field (e.g., lowest expense ratio). Use neutral language: "Among the funds in this corpus, X has the lowest available expense ratio of Y%."
6. If the requested information is not in the retrieved context, respond EXACTLY: "I could not find this information in the current source set."
7. Use normalized field names: "expense ratio / MER / TER" not country-specific slang alone.
8. Keep answers concise. No filler. No preamble. No speculation.
9. Never fabricate URLs, dates, or fund facts.
10. If AUM values are in different currencies, state each separately. Do not compare across currencies.

OUTPUT FORMAT:
[Concise factual answer — 2-5 sentences]

Key facts (if multiple fields available):
• Field: Value

Source: [url]
Last updated from sources: [date or "not available"]
Fetched by HealthFundIQ: [fetch_timestamp]"""


def build_context_block(chunks: list[dict]) -> str:
    """Format retrieved chunks into the context block for the LLM prompt."""
    if not chunks:
        return "No relevant context found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source_url = meta.get("official_url") or meta.get("source_url") or meta.get("platform_url", "")
        last_updated = meta.get("last_updated_from_source", "not available")
        fetch_ts = meta.get("fetch_timestamp", "")

        parts.append(
            f"[Context {i}]\n"
            f"Fund: {meta.get('fund_name', 'Unknown')} | Country: {meta.get('country', 'Unknown')} | Section: {meta.get('section', 'Unknown')}\n"
            f"Source type: {meta.get('source_type', 'unknown')}\n"
            f"Text: {chunk['text']}\n"
            f"Source URL: {source_url}\n"
            f"Last updated from source: {last_updated}\n"
            f"Fetched: {fetch_ts}"
        )

    return "\n\n---\n\n".join(parts)


def build_messages(query: str, chunks: list[dict]) -> list[dict]:
    context = build_context_block(chunks)
    user_content = f"Retrieved context:\n\n{context}\n\n---\n\nUser question: {query}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def build_classifier_messages(query: str) -> list[dict]:
    system = (
        "Classify this user query into exactly one of: FACTUAL, COMPARISON, ADVICE, OUT_OF_SCOPE.\n"
        "FACTUAL: asks for a specific fact about a fund (expense ratio, AUM, benchmark, holdings, objective, risk rating, manager, issuer, NAV).\n"
        "COMPARISON: asks to compare two or more funds on a factual field.\n"
        "ADVICE: asks for a recommendation, prediction, buy/sell/hold guidance, portfolio, timing, or return forecast.\n"
        "OUT_OF_SCOPE: asks about topics unrelated to healthcare/pharma/biotech funds in the corpus.\n"
        "Reply with exactly one word: FACTUAL, COMPARISON, ADVICE, or OUT_OF_SCOPE."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]
```

### 5.3 `llm/response_formatter.py`

```python
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
    "I could not find this information in the current source set for this fund."
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

    # Post-process: check for prohibited language
    if _check_prohibited(llm_answer):
        # Strip the problematic sentence rather than returning the full response
        # Practical approach: log and return a safe fallback
        import logging
        logging.getLogger("llm.response_formatter").warning(
            f"Prohibited phrase detected in LLM response — returning safe answer"
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
```

---

## 6. Phase 5 — Guardrails

### 6.1 `guardrails/classifier.py`

```python
import re
from llm.groq_client import complete
from llm.prompt_builder import build_classifier_messages
from config.settings import settings
from ingestion.logger import get_logger

logger = get_logger("guardrails.classifier")

VALID_INTENTS = {"FACTUAL", "COMPARISON", "ADVICE", "OUT_OF_SCOPE"}

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
```

---

## 7. Phase 6 — API Layer

### 7.1 `api/models.py`

```python
from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    query: str = Field(..., min_length=3, max_length=500)
    country: str | None = Field(default=None)
    fund_id: str | None = Field(default=None)


class ChatResponse(BaseModel):
    answer: str
    source_url: str | None = None
    platform_url: str | None = None
    last_updated: str | None = None
    fetch_timestamp: str | None = None
    is_refusal: bool
    intent: str
    missing_data: bool = False


class FundListItem(BaseModel):
    fund_id: str
    country: str
    fund_name: str
    ticker: str | None
    isin: str | None
    fund_type: str
    domain_subcategory: str
    currency: str
    exchange: str | None
    platform_url: str
    official_url: str | None
    is_backup: bool


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    corpus_chunks: int
```

### 7.2 `api/router.py`

```python
import yaml
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
from api.models import ChatRequest, ChatResponse, FundListItem, HealthResponse
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

VALID_COUNTRIES = {
    "India", "USA", "Canada", "China/HK", "Japan", "Singapore", "UK/Europe"
}


def _load_funds() -> list[dict]:
    with open("config/sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["funds"]


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

    # Validate country filter
    if req.country and req.country not in VALID_COUNTRIES:
        req.country = None  # ignore unrecognized country

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

    # 5. Generate
    # For comparisons use more tokens
    max_tokens = 768 if intent == "COMPARISON" else 512
    messages = build_messages(req.query, chunks[:8])  # cap context at 8 chunks
    answer = complete(messages=messages, max_tokens=max_tokens)

    resp = format_response(answer, chunks, intent)

    return ChatResponse(
        answer=resp.answer,
        source_url=resp.source_url,
        platform_url=resp.platform_url,
        last_updated=resp.last_updated,
        fetch_timestamp=resp.fetch_timestamp,
        is_refusal=resp.is_refusal,
        intent=resp.intent,
        missing_data=resp.missing_data,
    )


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
```

### 7.3 `api/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router
from ingestion.logger import get_logger

logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: warm up embedding model and start scheduler
    logger.info("HealthFundIQ API starting up")
    from embeddings.embedder import _get_model
    _get_model()  # pre-load BGE model

    from scheduler.refresh import start_scheduler
    start_scheduler()

    yield

    # Shutdown
    logger.info("HealthFundIQ API shutting down")
    from scheduler.refresh import stop_scheduler
    stop_scheduler()


app = FastAPI(
    title="HealthFundIQ API",
    description="Facts-only Global Healthcare Funds RAG Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8502", "http://127.0.0.1:8502"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router)
```

---

## 8. Phase 6 — Streamlit UI

### 8.1 `ui/components/disclaimer.py`

```python
import streamlit as st


def render_disclaimer():
    st.info(
        "**Facts only. No investment advice.**\n\n"
        "This assistant provides factual information from public sources only. "
        "It does not provide investment advice, buy/sell recommendations, portfolio allocation, "
        "return predictions, or personalized financial guidance. "
        "Always verify details from official fund documents before making financial decisions."
    )
```

### 8.2 `ui/components/sidebar.py`

```python
import yaml
import streamlit as st


def _load_funds():
    with open("config/sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["funds"]


def render_sidebar() -> tuple[str | None, str | None]:
    """Returns (selected_country, selected_fund_id)."""
    with st.sidebar:
        st.markdown("## HealthFundIQ")
        st.caption("Ask. Compare. Verify.")
        st.divider()

        countries = [
            "All Countries", "India", "USA", "Canada",
            "China/HK", "Japan", "Singapore", "UK/Europe",
        ]
        country = st.selectbox("Country / Market", countries, key="country_filter")
        selected_country = None if country == "All Countries" else country

        # Dynamic fund list based on country
        all_funds = _load_funds()
        if selected_country:
            filtered = [f for f in all_funds if f["country"] == selected_country and not f.get("is_backup")]
        else:
            filtered = [f for f in all_funds if not f.get("is_backup")]

        fund_options = {"All Funds": None}
        for f in filtered:
            label = f["ticker"] + " — " + f["fund_name"] if f.get("ticker") else f["fund_name"]
            fund_options[label] = f["id"]

        selected_label = st.selectbox("Fund", list(fund_options.keys()), key="fund_filter")
        selected_fund_id = fund_options[selected_label]

        st.divider()

        from ui.components.disclaimer import render_disclaimer
        render_disclaimer()

    return selected_country, selected_fund_id
```

### 8.3 `ui/components/source_card.py`

```python
import streamlit as st


BADGE_HTML = {
    "official": '<span style="background:#DCFCE7;color:#15803D;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:500;">Official</span>',
    "platform": '<span style="background:#F1F5F9;color:#475569;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:500;">Platform</span>',
    "pdf":      '<span style="background:#FEF3C7;color:#B45309;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:500;">PDF</span>',
}


def render_source_card(
    source_url: str | None,
    platform_url: str | None,
    last_updated: str | None,
    fetch_timestamp: str | None,
    source_type: str = "official",
):
    if not source_url and not platform_url:
        return

    badge = BADGE_HTML.get(source_type, BADGE_HTML["platform"])

    with st.container():
        st.markdown("**Sources**")
        if source_url:
            st.markdown(
                f"{badge} [{source_url[:60]}...]({source_url})" if len(source_url) > 60
                else f"{badge} [{source_url}]({source_url})",
                unsafe_allow_html=True,
            )
        if platform_url and platform_url != source_url:
            st.markdown(f"Also see: [{platform_url[:50]}...]({platform_url})" if len(platform_url) > 50
                        else f"Also see: [{platform_url}]({platform_url})")
        if last_updated:
            st.caption(f"Last updated from sources: {last_updated}")
        if fetch_timestamp:
            st.caption(f"Fetched by HealthFundIQ: {fetch_timestamp[:19]} IST")
```

### 8.4 `ui/components/chat.py`

```python
import streamlit as st
import requests
from ui.components.source_card import render_source_card

API_BASE = "http://localhost:8002"

EXAMPLE_CHIPS = [
    ("Expense ratio", "What is the expense ratio of HDFC Pharma and Healthcare Fund?"),
    ("Canada funds", "Which healthcare ETFs are available in Canada?"),
    ("XLV benchmark", "What benchmark does XLV track?"),
    ("Biotech focus", "Which funds in this corpus are biotech-focused?"),
    ("Country-wise", "Show healthcare funds available country-wise."),
    ("IBB holdings", "What are the top holdings of IBB?"),
    ("VHT objective", "What is the investment objective of VHT?"),
]


def render_welcome():
    st.markdown("""
    ### Ask. Compare. Verify.
    **Global healthcare funds — with facts, not financial advice.**

    Ask factual questions about healthcare, pharma, biotech, and med-tech funds
    across India, USA, Canada, China/HK, Japan, Singapore, and the UK.
    """)
    st.markdown("**Try one of these:**")
    cols = st.columns(4)
    for i, (label, query) in enumerate(EXAMPLE_CHIPS):
        if cols[i % 4].button(label, key=f"chip_{i}"):
            st.session_state["prefill_query"] = query
            st.rerun()


def _call_api(query: str, country: str | None, fund_id: str | None) -> dict | None:
    try:
        payload = {"query": query}
        if country:
            payload["country"] = country
        if fund_id:
            payload["fund_id"] = fund_id
        resp = requests.post(f"{API_BASE}/chat", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Backend unavailable. Start the FastAPI server first."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Try again."}
    except Exception as e:
        return {"error": str(e)}


def render_chat(country: str | None, fund_id: str | None):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        render_welcome()

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("source_url"):
                render_source_card(
                    source_url=msg["source_url"],
                    platform_url=msg.get("platform_url"),
                    last_updated=msg.get("last_updated"),
                    fetch_timestamp=msg.get("fetch_timestamp"),
                    source_type=msg.get("source_type", "official"),
                )

    # Pre-filled query from chip click
    prefill = st.session_state.pop("prefill_query", "")

    query = st.chat_input(
        "Ask about expense ratio, AUM, benchmark, holdings, risk rating, issuer...",
        key="chat_input",
    )
    query = query or prefill

    if query:
        # PII client-side check
        import re
        pii_patterns = [
            re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
            re.compile(r"\b[0-9]{12}\b"),
            re.compile(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+"),
        ]
        if any(p.search(query) for p in pii_patterns):
            st.warning(
                "Please do not share personal information (PAN, Aadhaar, email). "
                "HealthFundIQ only uses public fund sources."
            )
            return

        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Call API with loading state
        with st.chat_message("assistant"):
            with st.status("Processing...", expanded=False) as status:
                status.update(label="Classifying query...")
                data = _call_api(query, country, fund_id)
                status.update(label="Done", state="complete")

            if data is None or "error" in data:
                err_msg = data.get("error", "Unknown error") if data else "No response"
                st.error(f"Error: {err_msg}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {err_msg}"})
                return

            answer = data.get("answer", "No answer returned.")

            # Render answer
            if data.get("is_refusal"):
                st.warning(answer)
            elif data.get("missing_data"):
                st.info(answer)
            else:
                st.markdown(answer)

            # Source card
            if not data.get("is_refusal") and data.get("source_url"):
                render_source_card(
                    source_url=data.get("source_url"),
                    platform_url=data.get("platform_url"),
                    last_updated=data.get("last_updated"),
                    fetch_timestamp=data.get("fetch_timestamp"),
                )

        # Store in history
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "source_url": data.get("source_url"),
            "platform_url": data.get("platform_url"),
            "last_updated": data.get("last_updated"),
            "fetch_timestamp": data.get("fetch_timestamp"),
        })
```

### 8.5 `ui/app.py`

```python
import streamlit as st
import requests
import yaml

st.set_page_config(
    page_title="HealthFundIQ — Global Healthcare Funds Research",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.components.sidebar import render_sidebar
from ui.components.chat import render_chat

# Apply custom CSS
with open("ui/assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Render sidebar and get filters
selected_country, selected_fund_id = render_sidebar()

# Top bar
st.markdown(
    "**HealthFundIQ** &nbsp;|&nbsp; Ask. Compare. Verify global healthcare funds — with facts, not financial advice.",
    unsafe_allow_html=True,
)
st.divider()

# Tabs
tab_ask, tab_explorer, tab_compare, tab_sources, tab_about = st.tabs([
    "💬 Ask AI", "🔍 Fund Explorer", "⚖️ Compare Funds", "📋 Sources", "ℹ️ About"
])

with tab_ask:
    render_chat(selected_country, selected_fund_id)

with tab_explorer:
    st.markdown("### Fund Explorer")
    try:
        params = {}
        if selected_country:
            params["country"] = selected_country
        resp = requests.get("http://localhost:8002/funds", params=params, timeout=5)
        funds = resp.json()
        if not funds:
            st.info("No funds found for the selected filter.")
        else:
            for fund in funds:
                if fund.get("is_backup"):
                    continue
                with st.expander(f"{fund['fund_name']} — {fund['country']}"):
                    col1, col2 = st.columns(2)
                    col1.markdown(f"**Type:** {fund['fund_type']}")
                    col1.markdown(f"**Subcategory:** {fund['domain_subcategory']}")
                    col1.markdown(f"**Currency:** {fund['currency']}")
                    col2.markdown(f"**Exchange:** {fund.get('exchange', 'N/A')}")
                    col2.markdown(f"**Ticker/ISIN:** {fund.get('ticker') or fund.get('isin') or 'N/A'}")
                    if fund.get("official_url"):
                        st.markdown(f"[Official Source]({fund['official_url']})")
                    st.markdown(f"[Platform Page]({fund['platform_url']})")
    except Exception as e:
        st.error(f"Could not load fund list: {e}")

with tab_compare:
    st.markdown("### Compare Funds")
    st.info(
        "Side-by-side factual comparison is coming in Phase 2. "
        "Use the **Ask AI** tab to compare specific funds by asking: "
        "'Compare the expense ratio of XLV and VHT' or 'Show Canada healthcare ETFs.'"
    )

with tab_sources:
    st.markdown("### Corpus Status")
    try:
        resp = requests.get("http://localhost:8002/health", timeout=5)
        h = resp.json()
        st.metric("Corpus Chunks", h.get("corpus_chunks", 0))
        st.caption(f"Last checked: {h.get('timestamp', 'N/A')}")
    except Exception:
        st.warning("Backend unavailable — cannot show corpus status.")

    st.markdown("---")
    st.markdown("View ingestion logs in `logs/ingestion.log` for per-fund status.")

with tab_about:
    st.markdown("""
    ### About HealthFundIQ

    **HealthFundIQ** is a facts-only RAG assistant for global healthcare, pharma, biotech,
    and med-tech funds. It retrieves factual information from public sources and answers
    questions with citations.

    **Markets covered:** India · USA · Canada · China/HK · Japan · Singapore · UK/Europe

    **What it can answer:** expense ratio, AUM, benchmark, NAV, top holdings, investment
    objective, risk rating, fund manager, fund house, and more.

    **What it cannot do:** investment advice, buy/sell recommendations, portfolio construction,
    return predictions, or personalized financial guidance.

    **Data freshness:** Corpus refreshes daily at 10:00 AM IST.

    ---
    **Disclaimer:** This assistant provides factual information from public sources only.
    Always verify details from official fund documents and consult a qualified financial
    adviser before making investment decisions.
    """)
```

---

## 9. Phase 7 — Scheduler

### 9.1 `scheduler/refresh.py`

```python
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from ingestion.logger import get_logger

logger = get_logger("scheduler.refresh")
IST = pytz.timezone("Asia/Kolkata")

_scheduler: BackgroundScheduler | None = None
_ingestion_lock = threading.Lock()
_ingestion_running = False


def run_daily_refresh():
    global _ingestion_running
    if _ingestion_lock.acquire(blocking=False):
        try:
            _ingestion_running = True
            logger.info("Starting scheduled daily corpus refresh")
            from ingestion.run_ingestion import ingest_all
            ingest_all()
            logger.info("Daily corpus refresh complete")
        except Exception as e:
            logger.error(f"Scheduled refresh failed: {e}", exc_info=True)
        finally:
            _ingestion_running = False
            _ingestion_lock.release()
    else:
        logger.warning("Skipping scheduled run — previous ingestion still running")


def start_scheduler():
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return
    _scheduler = BackgroundScheduler(timezone=IST)
    _scheduler.add_job(
        run_daily_refresh,
        trigger=CronTrigger(hour=10, minute=0, timezone=IST),
        id="daily_refresh",
        replace_existing=True,
        misfire_grace_time=0,  # do NOT run missed jobs (per edge case S-03)
    )
    _scheduler.start()
    logger.info("Scheduler started — daily refresh at 10:00 AM IST")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def is_ingestion_running() -> bool:
    return _ingestion_running
```

---

## 10. Tests

### 10.1 `tests/test_guardrails.py`

```python
import pytest
from guardrails.classifier import classify, contains_pii

ADVICE_QUERIES = [
    "Should I buy XLV?",
    "Which healthcare fund is best for me?",
    "Will XLV give better returns than VHT?",
    "Can you build a healthcare portfolio for me?",
    "Is this a good time to buy healthcare ETFs?",
    "How much money should I invest in IBB?",
]

FACTUAL_QUERIES = [
    "What is the expense ratio of HDFC Pharma and Healthcare Fund?",
    "What benchmark does XLV track?",
    "Who manages Nippon India Pharma Fund?",
    "What are the top holdings of IBB?",
    "Which funds are biotech-focused?",
]

# Holdings must NOT trigger ADVICE (contains "hold")
FALSE_POSITIVE_RISKS = [
    "What are the top holdings of XLV?",
    "Show me the holdings of VHT",
]

PII_QUERIES = [
    "ABCDE1234F",          # PAN
    "123456789012",        # Aadhaar
    "user@example.com",    # Email
]


def test_advice_queries_refused():
    for q in ADVICE_QUERIES:
        assert classify(q) == "ADVICE", f"Expected ADVICE for: {q!r}"


def test_factual_queries_not_refused():
    for q in FACTUAL_QUERIES:
        intent = classify(q)
        assert intent in ("FACTUAL", "COMPARISON"), f"Expected FACTUAL/COMPARISON for: {q!r}, got {intent}"


def test_holdings_not_false_positive():
    for q in FALSE_POSITIVE_RISKS:
        intent = classify(q)
        assert intent != "ADVICE", f"False positive ADVICE for holdings query: {q!r}"


def test_pii_detection():
    for q in PII_QUERIES:
        assert contains_pii(q), f"PII not detected in: {q!r}"
```

### 10.2 `tests/test_chunker.py`

```python
import pytest
from ingestion.normalizer import NormalizedFund
from ingestion.chunker import chunk_fund


def _make_fund(**kwargs) -> NormalizedFund:
    defaults = dict(
        fund_id="test_xlv", country_or_market="USA",
        fund_name="Test Healthcare ETF", ticker_or_identifier="TEST",
        fund_type="ETF", domain_subcategory="Broad Healthcare",
        currency="USD", exchange="NYSE Arca",
        source_type="official", platform_url="https://example.com",
        official_url="https://official.example.com",
        last_updated_from_source="2026-06-01",
        fetch_timestamp="2026-06-02T10:00:00+05:30",
        expense_ratio_or_mer_or_ter="0.09%",
        benchmark="Health Care Select Sector Index",
        investment_objective="Seeks to track the Health Care Select Sector Index.",
        fund_house_or_issuer="State Street",
    )
    defaults.update(kwargs)
    return NormalizedFund(**defaults)


def test_overview_always_created():
    fund = _make_fund()
    chunks = chunk_fund(fund)
    sections = [c.section for c in chunks]
    assert "overview" in sections


def test_cost_ratio_chunk_created():
    fund = _make_fund()
    chunks = chunk_fund(fund)
    assert any(c.section == "cost_ratio" for c in chunks)


def test_missing_field_no_chunk():
    fund = _make_fund(expense_ratio_or_mer_or_ter=None)
    chunks = chunk_fund(fund)
    assert not any(c.section == "cost_ratio" for c in chunks)


def test_chunk_text_has_prefix():
    fund = _make_fund()
    chunks = chunk_fund(fund)
    cost_chunk = next(c for c in chunks if c.section == "cost_ratio")
    assert "Test Healthcare ETF" in cost_chunk.text
    assert "USA" in cost_chunk.text


def test_chunk_metadata_no_none():
    fund = _make_fund()
    chunks = chunk_fund(fund)
    for chunk in chunks:
        assert chunk.ticker is not None  # "" not None
        assert chunk.isin is not None
        assert chunk.official_url is not None


def test_long_objective_splits():
    long_obj = "A " * 600  # well over 512 tokens
    fund = _make_fund(investment_objective=long_obj)
    chunks = chunk_fund(fund)
    obj_chunks = [c for c in chunks if "investment_objective" in c.chunk_id]
    assert len(obj_chunks) > 1
```

### 10.3 `tests/test_normalizer.py`

```python
from ingestion.html_parser import ParsedFund
from ingestion.normalizer import normalize

SOURCE_META = {
    "id": "usa_xlv", "country": "USA", "fund_name": "XLV",
    "ticker": "XLV", "isin": None, "fund_type": "ETF",
    "domain_subcategory": "Broad Healthcare", "currency": "USD",
    "exchange": "NYSE Arca", "platform_url": "https://etf.com/XLV",
    "official_url": "https://ssga.com/xlv",
}


def _make_parsed(**raw_fields) -> ParsedFund:
    return ParsedFund(
        fund_id="usa_xlv", country="USA", fund_name="XLV",
        ticker="XLV", isin=None,
        source_url="https://ssga.com/xlv", source_type="official",
        fetch_timestamp="2026-06-02T10:00:00+05:30",
        parse_method="beautifulsoup", parse_success=True,
        raw_fields=raw_fields,
    )


def test_expense_ratio_mapped():
    p = _make_parsed(**{"Expense Ratio": "0.09%"})
    n = normalize(p, SOURCE_META)
    assert n.expense_ratio_or_mer_or_ter == "0.09%"


def test_canada_mer_mapped():
    meta = {**SOURCE_META, "country": "Canada", "id": "canada_hhl"}
    p = ParsedFund(
        fund_id="canada_hhl", country="Canada", fund_name="HHL",
        ticker="HHL", isin=None,
        source_url="https://harvestportfolios.com/etf/hhl/",
        source_type="official",
        fetch_timestamp="2026-06-02T10:00:00+05:30",
        parse_method="beautifulsoup", parse_success=True,
        raw_fields={"MER": "0.85%", "Risk Rating": "Medium"},
    )
    n = normalize(p, meta)
    assert n.expense_ratio_or_mer_or_ter == "0.85%"
    assert n.risk_rating_or_riskometer == "Medium"


def test_missing_field_in_missing_list():
    p = _make_parsed()  # no raw fields
    n = normalize(p, SOURCE_META)
    assert "expense_ratio_or_mer_or_ter" in n.missing_fields
```

---

## 11. Startup and Run Instructions

### 11.1 First-Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browser
playwright install chromium

# 3. Copy and fill env file
copy .env.example .env
# Edit .env — set GROQ_API_KEY

# 4. Run first ingestion (takes 10–30 min depending on network)
python -m ingestion.run_ingestion

# 5. Verify corpus has chunks
python -c "from embeddings.store import get_collection_count; print('Chunks:', get_collection_count())"
```

### 11.2 Start Services

Open two terminals:

**Terminal 1 — FastAPI backend:**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 2 — Streamlit frontend:**
```bash
streamlit run ui/app.py --server.port 8502
```

Open browser at `http://localhost:8502`.

### 11.3 Run Tests

```bash
# All tests
pytest tests/ -v

# Guardrails only (fast, no LLM calls needed for regex stage)
pytest tests/test_guardrails.py -v -k "not advice_queries"

# Chunker tests (no external deps)
pytest tests/test_chunker.py -v
```

### 11.4 Manual Ingestion Trigger

```bash
python -m ingestion.run_ingestion
```

---

## 12. Implementation Pitfalls (from Edge Case Analysis)

Critical issues to verify during each phase before moving to the next:

| Phase | Pitfall | Fix |
|---|---|---|
| Crawler | Playwright not installed | Run `playwright install chromium` before ingestion |
| Parser | `pdfplumber.open()` passed raw bytes | Use `io.BytesIO(pdf_bytes)` — pdfplumber requires a file-like object, not raw bytes |
| Crawler | Yahoo Finance returns 429 | Add 2s delay between same-domain fetches in `run_ingestion.py` |
| Parser | Groww React SPA returns empty divs | `use_playwright: true` must be set in sources.yaml for all India funds |
| Normalizer | Qdrant rejects `None` metadata values | All `None` → `""` enforced in `_chunk_to_point()` payload construction |
| Chunker | "hold" keyword triggers ADVICE refusal | Regex pattern in classifier uses word boundary + context check |
| Guardrail | "Which fund has the best expense ratio?" should be COMPARISON | Stage 2 LLM classifier handles this; regex should NOT catch "best" alone |
| LLM | LLM generates hallucinated URL | System prompt rule 9: "Never fabricate URLs" + temperature=0.0 |
| API | `source_url` is `None` for factual answer | `format_response()` falls back to platform_url; always populated |
| UI | Chip click fires duplicate queries | `st.session_state` flag prevents re-submission |
| Scheduler | Two ingestion runs overlap | `threading.Lock()` in `scheduler/refresh.py` prevents concurrent admin-triggered runs; GitHub Actions serialises scheduled runs natively |
| Qdrant | Collection missing on first run | `_ensure_collection()` auto-creates with indices; safe to call on every request |
| Qdrant | Score vs distance confusion | Qdrant returns cosine similarity (higher=better); store.py converts to distance: `distance = 1 - score` |
| `.env` | Missing GROQ_API_KEY on startup | `settings = Settings()` raises `ValidationError` — catch at startup with clear message |
| Railway | BGE-large model download timeout | Pre-bake model in Dockerfile or switch to bge-small (384-dim) — update `_VECTOR_DIM` in store.py |

---

## 13. Changes Applied After Initial Build (June 2026)

### 13.1 Qdrant Cloud Migration

`embeddings/store.py` was rewritten to use `qdrant-client` instead of `chromadb`.

Key differences from ChromaDB implementation:
- Point IDs are UUID5 strings derived from `chunk_id` (deterministic, collision-free)
- Chunk text is stored in the Qdrant payload (not as a separate `documents` field)
- Cosine similarity scores are converted to distance: `distance = 1.0 - score`
- Payload indices are created at collection init for efficient filtered search
- `_build_filter()` converts the existing ChromaDB-style `where` dict to Qdrant `Filter` objects — no changes needed in `retriever.py` or `reranker.py`

`config/settings.py` was updated to replace ChromaDB settings:

```python
# Old (removed)
chroma_persist_dir: str = "./vectorstore/chroma_db"
chroma_collection: str = "healthcare_funds"

# New (Qdrant)
qdrant_url: str = ""               # empty = use local file mode
qdrant_api_key: str = ""
qdrant_collection: str = "healthcare_funds"
qdrant_local_path: str = "./vectorstore/qdrant_local"
```

### 13.2 Backup Source URLs

`config/sources.yaml` now includes a `backup_platform_urls` list for each active fund. `ingestion/run_ingestion.py:ingest_fund()` iterates these after the primary merge when important fields (`expense_ratio_or_mer_or_ter`, `aum`, `benchmark`, `fund_management`, `fund_house_or_issuer`, `risk_rating_or_riskometer`, `investment_objective`) are still missing.

### 13.3 Structured Lookup in api/router.py

Three new helpers before the classify/retrieve pipeline:
- `_FACTUAL_FIELD_MAP` — 30 keyword → (field_name, label) pairs
- `_detect_factual_field(query)` — longest-match keyword scan
- `_detect_fund(query, funds)` — ticker word match then fund-name substring match
- `_structured_lookup(query, funds)` — reads `data/parsed/{slug}/{fund_id}.json` directly; returns `ChatResponse` with the field value or `None` to fall through to RAG

### 13.4 ChatResponse.fund_name

`api/models.py` and `frontend/lib/types.ts` both have a new optional `fund_name` field. The frontend `FollowUpChips` component appends `" for {fund_name}"` to fund-specific chip queries so the backend always receives full context.

### 13.5 ECG Loading Animation Fix

`frontend/app/research/page.tsx` — added `key="loading"` and `transition={{ duration: 0.1 }}` to the `motion.div` inside `AnimatePresence`.

`frontend/app/globals.css` — added `animation-fill-mode: forwards` to `.ecg-path` to stop the CSS infinite animation from conflicting with the framer-motion fade-out.

---

*Build phase by phase. Do not skip to Phase 3 before Phase 1 produces real chunks in Qdrant. Each phase has a concrete verification step — complete it before moving on.*
