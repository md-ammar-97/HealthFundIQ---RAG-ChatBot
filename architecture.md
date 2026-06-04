# FinanceBot — Global Healthcare Funds RAG Assistant: Architecture

---

## 1. System Overview

FinanceBot is a seven-layer RAG pipeline. Each layer has a single responsibility and a clean handoff to the next.

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Browser / UI)                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP (Streamlit)
┌───────────────────────────────▼─────────────────────────────────┐
│                     STREAMLIT FRONTEND                          │
│   Country filter · Fund filter · Chat input · Source display    │
└───────────────────────────────┬─────────────────────────────────┘
                                │ REST API call
┌───────────────────────────────▼─────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│   /chat endpoint · Guardrail classifier · Orchestrator          │
└──────────┬────────────────────┬────────────────────────────────-┘
           │                   │
    [Advice query]      [Factual query]
           │                   │
    Refusal handler     ┌──────▼──────────────────────────────────┐
           │            │         RETRIEVER                       │
           │            │  Metadata filter → Semantic search      │
           │            │  ChromaDB / Qdrant vector store         │
           │            └──────┬──────────────────────────────────┘
           │                   │ Top-k chunks + metadata
           │            ┌──────▼──────────────────────────────────┐
           │            │      LLM RESPONSE GENERATOR             │
           │            │  Groq API · llama-3.3-70b-versatile     │
           │            │  Prompt = system + chunks + query       │
           │            └──────┬──────────────────────────────────┘
           │                   │ Answer + source + timestamp
           └───────────────────▼
                       Response to UI

┌─────────────────────────────────────────────────────────────────┐
│               INGESTION PIPELINE (offline / scheduled)          │
│  Crawler → Parser → Normalizer → Chunker → Embedder → Store    │
└─────────────────────────────────────────────────────────────────┘
                  ▲ triggered daily at 10:00 AM IST
┌─────────────────┴───────────────────────────────────────────────┐
│                        SCHEDULER                                │
│                   APScheduler (in-process)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure

```
FinanceBot/
│
├── Problem__Statement.md         # Original requirements
├── context.md                    # Detailed project context
├── architecture.md               # This file
│
├── .env                          # API keys and config (not committed)
├── .env.example                  # Template for .env
├── requirements.txt
├── README.md
│
├── config/
│   ├── sources.yaml              # Master corpus: all fund URLs + metadata
│   ├── settings.py               # Loads .env, exposes typed config object
│   └── normalization.yaml        # Term normalization map per country
│
├── ingestion/
│   ├── crawler.py                # Fetches HTML and PDF URLs
│   ├── html_parser.py            # BeautifulSoup + Playwright extraction
│   ├── pdf_parser.py             # pdfplumber extraction for PDF factsheets
│   ├── normalizer.py             # Maps country-specific terms to normalized fields
│   ├── chunker.py                # Splits extracted text into semantic chunks
│   └── run_ingestion.py          # CLI entry point: python -m ingestion.run_ingestion
│
├── embeddings/
│   ├── embedder.py               # BGE model wrapper; encodes chunks
│   ├── store.py                  # ChromaDB / Qdrant read/write operations
│   └── schema.py                 # Chunk dataclass + metadata field definitions
│
├── retrieval/
│   ├── retriever.py              # Metadata filter + semantic similarity query
│   └── reranker.py               # Optional: boost official-source chunks
│
├── llm/
│   ├── groq_client.py            # Groq API wrapper
│   ├── prompt_builder.py         # Assembles system + context + query prompt
│   └── response_formatter.py    # Formats answer + source + timestamp
│
├── guardrails/
│   ├── classifier.py             # Query intent classifier (factual / advice / OOS)
│   └── refusal.py                # Returns polite refusal strings
│
├── api/
│   ├── main.py                   # FastAPI app; defines /chat and /health
│   ├── models.py                 # Pydantic request/response models
│   └── router.py                 # Route definitions
│
├── ui/
│   ├── app.py                    # Streamlit app entry point
│   ├── components/
│   │   ├── sidebar.py            # Country + fund filters
│   │   ├── chat.py               # Chat input + answer display
│   │   ├── source_card.py        # Source link + timestamp card
│   │   └── disclaimer.py        # Static disclaimer banner
│   └── assets/
│       └── styles.css            # Optional custom CSS
│
├── scheduler/
│   └── refresh.py                # APScheduler job; runs ingestion daily at 10:00 AM IST
│
├── data/
│   ├── raw/                      # Raw HTML / PDF files saved per fetch
│   │   └── <country>/<ticker>/   # e.g., data/raw/india/hdfc_pharma/
│   ├── parsed/                   # Cleaned text per fund (JSON)
│   └── chunks/                   # Chunked + metadata-tagged records (JSON, for audit)
│
├── vectorstore/
│   └── chroma_db/                # ChromaDB local persistence directory
│
├── logs/
│   ├── ingestion.log
│   ├── retrieval.log
│   └── scheduler.log
│
└── tests/
    ├── test_crawler.py
    ├── test_normalizer.py
    ├── test_chunker.py
    ├── test_retriever.py
    ├── test_guardrails.py
    └── test_api.py
```

---

## 3. Configuration Layer (`config/`)

### 3.1 `sources.yaml` — Master Corpus Registry

Every fund in the corpus is declared here. This is the single source of truth for ingestion.

```yaml
funds:
  - id: india_hdfc_pharma
    country: India
    fund_name: HDFC Pharma and Healthcare Fund Direct Growth
    ticker: null
    isin: null
    fund_type: Mutual Fund
    domain_subcategory: Pharma / Broad Healthcare
    currency: INR
    exchange: BSE / NSE
    platform_url: https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth
    official_url: https://www.hdfcfund.com/explore/mutual-funds/hdfc-pharma-and-healthcare-fund/direct
    official_url_validated: false
    use_playwright: true
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false
    backup_platform_urls:                  # tried in order when primary parse leaves important fields missing
      - https://www.etmoney.com/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth/44167
      - https://www.valueresearchonline.com/funds/43786/hdfc-pharma-and-healthcare-fund-direct-plan/

  - id: usa_xlv
    country: USA
    fund_name: Health Care Select Sector SPDR ETF
    ticker: XLV
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: NYSE Arca
    platform_url: https://www.etf.com/XLV
    official_url: https://www.ssga.com/us/en/intermediary/etfs/state-street-health-care-select-sector-spdr-etf-xlv
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false
    backup_platform_urls:
      - https://stockanalysis.com/etf/xlv/
      - https://etfdb.com/etf/XLV/
      - https://finance.yahoo.com/quote/XLV/
  # ... all 34 entries — see config/sources.yaml for full list
```

### 3.2 `normalization.yaml` — Term Mapping

```yaml
cost_ratio:
  india: [expense ratio, total expense ratio]
  usa: [expense ratio, gross expense ratio, net expense ratio]
  canada: [MER, management expense ratio, management fee]
  uk_europe: [TER, total expense ratio, ongoing charge, OCF]

risk:
  india: [riskometer, risk level]
  usa: [risk level]
  canada: [risk rating]
  uk_europe: [SRRI, synthetic risk and reward indicator, risk indicator]

fund_size:
  india: [AUM, assets under management]
  usa: [net assets, AUM, total net assets]
  canada: [net assets, AUM]
  uk_europe: [fund size, total net assets, AUM]

fund_house:
  india: [AMC, asset management company, fund house]
  usa: [issuer, adviser, investment adviser]
  canada: [manager, issuer, management company]
  uk_europe: [issuer, asset manager, investment manager]
```

### 3.3 `settings.py` — Typed Config Object

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chroma_persist_dir: str = "./vectorstore/chroma_db"
    chroma_collection: str = "healthcare_funds"
    top_k_retrieval: int = 6
    scheduler_hour_ist: int = 10
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 4. Ingestion Pipeline (`ingestion/`)

### 4.1 Data Flow

```
sources.yaml
    │
    ▼
crawler.py          ── fetches URL ──► data/raw/<country>/<id>/page.html
    │                                  data/raw/<country>/<id>/factsheet.pdf
    ▼
html_parser.py      ── extracts fields ──► ParsedFund (dataclass)
pdf_parser.py       ── extracts fields ──► ParsedFund (dataclass)
    │
    ▼
normalizer.py       ── maps terms ──► NormalizedFund (all fields use normalized keys)
    │
    ▼
chunker.py          ── splits into ──► List[Chunk]  (one chunk per section)
    │
    ▼
embedder.py         ── encodes ──► List[Chunk + embedding vector]
    │
    ▼
store.py            ── upserts ──► ChromaDB collection
```

### 4.2 `crawler.py` — Fetch Strategy

```python
# Two fetch modes:
# 1. Static: requests + BeautifulSoup (fast, no JS)
# 2. Dynamic: Playwright headless browser (JS-rendered pages: Groww, some issuers)

def fetch(url: str, use_playwright: bool = False) -> str:
    ...

# Decision logic: try static first; if content < MIN_CONTENT_CHARS, retry with Playwright
# Rate limiting: 1-2 second delay between requests (respectful scraping)
# User-Agent: realistic browser UA string
# Retry: 3 attempts with exponential backoff
# PDF: download binary, save to data/raw/
```

JS-heavy pages (use Playwright):
- All Groww URLs (React SPA)
- Some issuer pages (Vanguard, iShares, HKEX)

Static pages (use requests):
- ETF.com
- TMX Money
- JustETF
- Yahoo Finance
- nextfunds.jp

### 4.3 `html_parser.py` — Field Extraction

```python
@dataclass
class ParsedFund:
    fund_id: str           # matches sources.yaml id
    country: str
    fund_name: str
    ticker: str | None
    raw_fields: dict       # key: country-specific label, value: extracted text
    source_url: str
    source_type: str       # "platform" or "official"
    fetch_timestamp: str   # ISO 8601
    parse_success: bool
    missing_fields: list[str]
```

Extraction uses a priority strategy:
1. Structured HTML (tables, definition lists, labeled divs).
2. CSS selector patterns specific to each platform (configured per platform in sources.yaml).
3. Regex fallback for common patterns (e.g., `Expense Ratio: 0.89%`).

### 4.4 `pdf_parser.py` — PDF Extraction (Singapore/Amova)

```python
# pdfplumber: best for tabular data in PDFs (fund factsheets)
# pypdf: fallback for simple text extraction
# Extraction targets: tables (holdings, sector exposure), text blocks (objective, risk)
```

### 4.5 `normalizer.py` — Term Normalization

```python
def normalize(parsed: ParsedFund, country: str) -> NormalizedFund:
    # Load normalization.yaml for this country
    # Map raw_fields keys to normalized field names
    # Store both: normalized_fields (clean) + raw_fields (audit)
    ...

@dataclass
class NormalizedFund:
    fund_id: str
    country_or_market: str
    fund_name: str
    ticker_or_identifier: str | None
    fund_type: str
    domain_subcategory: str
    nav_or_price: str | None
    aum: str | None
    expense_ratio_or_mer_or_ter: str | None  # normalized label, country value preserved
    minimum_investment: str | None
    minimum_sip: str | None
    exit_load_or_redemption_fee: str | None
    benchmark: str | None
    fund_management: str | None
    fund_house_or_issuer: str | None
    investment_objective: str | None
    risk_rating_or_riskometer: str | None
    top_10_holdings: list[str] | None
    sector_exposure: dict | None
    geographic_exposure: dict | None
    distribution_policy: str | None
    currency: str
    exchange: str | None
    documents: list[str] | None
    platform_url: str
    official_url: str | None
    last_updated_from_source: str | None
    fetch_timestamp: str
```

### 4.6 `chunker.py` — Semantic Chunking

Each fund is split into discrete section-level chunks. Each chunk is independently retrievable.

```python
SECTION_KEYS = [
    "overview",
    "cost_ratio",          # expense_ratio / MER / TER
    "risk",                # riskometer / risk rating / SRRI
    "benchmark",
    "investment_objective",
    "fund_management",
    "fund_house_or_issuer",
    "nav_or_price",
    "aum",
    "top_10_holdings",
    "sector_exposure",
    "geographic_exposure",
    "minimum_investment",
    "exit_load",
    "distribution_policy",
    "documents",
]

@dataclass
class Chunk:
    chunk_id: str           # "<fund_id>_<section>"
    fund_id: str
    section: str
    text: str               # the actual content
    # metadata (stored in ChromaDB alongside the embedding):
    country: str
    fund_name: str
    ticker: str | None
    domain_subcategory: str
    source_type: str        # "official" or "platform"
    source_url: str
    official_url: str | None
    last_updated_from_source: str | None
    fetch_timestamp: str
```

Chunking rules:
- One chunk per section per fund.
- Max chunk size: 512 tokens (split further if exceeded, preserving section label in each sub-chunk).
- Minimum chunk size: 20 tokens (discard if below — likely extraction failure).
- Prepend fund name and section label to chunk text for better embedding quality:
  `"[XLV | USA | Expense Ratio] The fund has a net expense ratio of 0.09%."`

---

## 5. Embeddings and Vector Store (`embeddings/`)

### 5.1 Embedding Model

| Option | Model | Dim | Use when |
|---|---|---|---|
| Default (v1) | `BAAI/bge-small-en-v1.5` | 384 | Resource-constrained; fast local inference |
| Upgrade | `BAAI/bge-base-en-v1.5` | 768 | Better retrieval quality |
| Max quality | `BAAI/bge-large-en-v1.5` | 1024 | High-resource machines |

All BGE models run locally via `sentence-transformers`. No external API cost.

BGE-specific instruction prefix (improves retrieval quality):
- Query: `"Represent this sentence for searching relevant passages: <query>"`
- Document: no prefix needed for BGE.

### 5.2 Qdrant Cloud Schema

Vector store: **Qdrant Cloud** (production) / Qdrant local file mode (dev)
Collection name: `healthcare_funds`
Vector dimension: 1024 (bge-large-en-v1.5) | Distance: Cosine

```python
# Each point in the Qdrant collection:
{
    "id": "<uuid5 derived from chunk_id>",   # deterministic UUID string
    "vector": [...],                          # float list, 1024-dim (bge-large)
    "payload": {
        "chunk_id": "usa_xlv_cost_ratio",
        "fund_id": "usa_xlv",
        "section": "cost_ratio",
        "country": "USA",
        "fund_name": "Health Care Select Sector SPDR ETF",
        "ticker": "XLV",
        "isin": "",
        "domain_subcategory": "Broad Healthcare",
        "fund_type": "ETF",
        "source_type": "official",
        "source_url": "https://www.ssga.com/...",
        "official_url": "https://www.ssga.com/...",
        "platform_url": "https://www.etf.com/XLV",
        "last_updated_from_source": "2026-06-01",
        "fetch_timestamp": "2026-06-02T10:00:00+05:30",
        "text": "[Health Care Select Sector SPDR ETF | USA | Expense Ratio]\n..."
    }
}
```

Payload indices created at collection init for efficient filtered search:
`fund_id`, `country`, `section`, `ticker`, `isin`, `source_type`, `domain_subcategory`

### 5.3 Upsert Strategy

On each scheduled refresh:
1. Fetch + parse + normalize + chunk each fund.
2. Upsert by deterministic UUID (derived from chunk_id) — overwrites stale points, adds new ones.
3. Do NOT delete-all and re-insert; use upsert to preserve chunks from sources that temporarily fail.
4. Log which chunks were updated vs unchanged.

---

## 6. Retrieval Layer (`retrieval/`)

### 6.1 Query Processing Flow

```
User query
    │
    ├─► PII check (server-side guard)
    │       └── PII detected → immediate refusal
    │
    ├─► Fund listing / total AUM short-circuits
    │       └── structured YAML response, skip retrieval
    │
    ├─► Structured lookup (deterministic — NEW)
    │       │   Detect factual field keyword + fund name/ticker in query
    │       │   Load data/parsed/{country}/{fund_id}.json directly
    │       └── field found → return value immediately (no LLM, no retrieval)
    │
    ├─► Guardrail classifier  (Section 7)
    │       ├── advice → Refusal (skip retrieval)
    │       └── factual / comparison → continue
    │
    ▼
Entity extractor
    │   Extract: fund name / ticker / country / field requested
    │   e.g., "What is the MER of HHL?" → {ticker: "HHL", country: "Canada", field: "cost_ratio"}
    │
    ▼
Metadata filter builder
    │   Build Qdrant filter from extracted entities
    │   e.g., {"country": "Canada", "ticker": "HHL", "section": "cost_ratio"}
    │
    ▼
Vector similarity search (top_k=6, default)
    │   Embed the query with BGE + instruction prefix
    │   Query Qdrant with payload filter + cosine similarity
    │
    ▼
Reranker
    │   Boost chunks where source_type == "official"
    │   Penalize chunks with missing last_updated_from_source
    │
    ▼
Confidence gate (≥2 chunks with distance < 0.75)
    │   Fail → missing_data response
    │
    ▼
Top-k chunks → LLM prompt builder → Groq → response
```

### 6.2 `retriever.py` — Core Logic

```python
def retrieve(
    query: str,
    country: str | None = None,
    fund_id: str | None = None,
    ticker: str | None = None,
    section: str | None = None,
    top_k: int = 6,
) -> list[Chunk]:
    where = {}
    if country:   where["country"] = country
    if fund_id:   where["fund_id"] = fund_id
    if ticker:    where["ticker"] = ticker
    if section:   where["section"] = section

    query_embedding = embedder.encode(f"Represent this sentence for searching relevant passages: {query}")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where if where else None,
    )
    return parse_results(results)
```

### 6.3 Country-Wise Comparison Queries

For queries like "Show healthcare funds country-wise" or "Which funds are biotech-focused?":
- Do NOT apply country filter.
- Apply section filter (e.g., `section: "overview"`).
- Retrieve top_k = 15 (more results, one per fund).
- Group results by country in response formatter.

---

## 7. Guardrails Layer (`guardrails/`)

### 7.1 Query Classification

Classification runs BEFORE retrieval. Two-stage approach:

**Stage 1 — Fast regex/keyword classifier (no LLM cost)**

Triggers refusal immediately on high-confidence advice keywords:

```python
ADVICE_PATTERNS = [
    r"\bshould i\b",
    r"\bwhich.*(best|better|recommend)\b",
    r"\bbuy\b|\bsell\b|\bhold\b",
    r"\bportfolio\b",
    r"\breturn(s)?\b.*(predict|expect|forecast|next year)\b",
    r"\bhow much.*(invest|put)\b",
    r"\bright time\b|\bgood time\b|\btiming\b",
    r"\brisk profile\b",
    r"\btax (plan|advice|saving)\b",
]
```

**Stage 2 — LLM classifier (for ambiguous queries)**

Used only when Stage 1 doesn't fire. Lightweight prompt:

```
System: Classify this user query into one of: FACTUAL, COMPARISON, ADVICE, OUT_OF_SCOPE.
A FACTUAL query asks for a specific fact about a fund (expense ratio, AUM, benchmark, etc.).
A COMPARISON query asks to compare two or more funds on a factual field.
An ADVICE query asks for a recommendation, prediction, or personalized guidance.
OUT_OF_SCOPE asks about topics unrelated to healthcare funds.
Reply with exactly one word: FACTUAL, COMPARISON, ADVICE, or OUT_OF_SCOPE.
User query: {query}
```

Model: `llama-3.1-8b-instant` on Groq (fast, low cost for classification).

### 7.2 Intent → Action Map

| Intent | Action |
|---|---|
| FACTUAL | Retrieve (with entity filter) → Generate answer |
| COMPARISON | Retrieve (multi-fund, no country filter) → Generate comparison |
| ADVICE | Return refusal immediately, no retrieval |
| OUT_OF_SCOPE | Return refusal immediately, no retrieval |

### 7.3 Refusal Strings

```python
REFUSAL_ADVICE = (
    "I can't provide investment advice or buy/sell recommendations. "
    "I can help with factual details such as expense ratio, AUM, benchmark, "
    "holdings, risk rating, investment objective, and official source documents. "
    "What factual information would you like to know?"
)

REFUSAL_OOS = (
    "This assistant only covers healthcare, pharma, biotech, and med-tech funds "
    "across India, USA, Canada, China, Hong Kong, Singapore, Japan, and the UK. "
    "I couldn't find a relevant fund question in your query."
)

MISSING_DATA = (
    "I could not find this information in the current source set for this fund."
)
```

---

## 8. LLM Response Generation (`llm/`)

### 8.1 Prompt Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ SYSTEM PROMPT (static, cached)                                  │
│  - Role: facts-only healthcare funds assistant                  │
│  - Hard rules: cite source, no advice, no hallucination         │
│  - Normalization reminder: use normalized field names           │
│  - Output format template                                       │
├─────────────────────────────────────────────────────────────────┤
│ CONTEXT BLOCK (dynamic, per query)                              │
│  - Retrieved chunk 1: [fund_name | country | section]           │
│    Text: ...                                                    │
│    Source: <url>  Last updated: <date>                          │
│  - Retrieved chunk 2: ...                                       │
│  - Retrieved chunk N: ...                                       │
├─────────────────────────────────────────────────────────────────┤
│ USER QUERY                                                      │
│  What is the expense ratio of HDFC Pharma and Healthcare Fund?  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 System Prompt (full)

```
You are a facts-only Global Healthcare Funds RAG Assistant.

RULES (never violate):
1. Answer ONLY from the retrieved context provided below. Never use your own knowledge or memory.
2. Every answer must include the Source URL from the context. Use the official_url if available; otherwise use the source_url.
3. Every answer must include "Last updated from sources" if the value is present in the context.
4. Do not provide investment advice, buy/sell recommendations, portfolio construction, return predictions, or personalized guidance. If the user asks for any of these, stop and return the refusal message.
5. Do not rank funds as "best" or "better" unless you are comparing a specific factual field (e.g., "which has the lowest expense ratio").
6. If the requested information is not present in the retrieved context, respond exactly: "I could not find this information in the current source set."
7. Use normalized field names in responses: "expense ratio / MER / TER" not country-specific slang.
8. Keep answers concise. No filler. No preamble.

OUTPUT FORMAT:
[Concise factual answer]

Source: [url]
Last updated from sources: [date or "not available"]
```

### 8.3 Groq API Call

```python
# Model: llama-3.3-70b-versatile (primary)
# Temperature: 0.0 (deterministic, factual)
# Max tokens: 512 (concise answers)
# Stop sequences: none needed
# Stream: optional (Streamlit supports streaming)
```

### 8.4 Response Formatter

```python
@dataclass
class BotResponse:
    answer: str
    source_url: str          # official_url preferred
    platform_url: str | None # shown as secondary link
    last_updated: str | None
    fetch_timestamp: str
    is_refusal: bool
    chunks_used: list[str]   # chunk_ids for audit
```

---

## 9. API Layer (`api/`)

### 9.1 Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Returns `{"status": "ok", "timestamp": "...", "corpus_chunks": N}` |
| POST | `/chat` | Main chat endpoint |
| GET | `/funds` | Returns full fund list from sources.yaml (non-backup funds) |
| GET | `/funds?country={country}` | Returns funds filtered by country (query parameter, not path parameter) |

### 9.2 `/chat` Request / Response

```python
# Request
class ChatRequest(BaseModel):
    query: str
    country: str | None = None    # optional filter from UI dropdown
    fund_id: str | None = None    # optional filter from UI dropdown

# Response
class ChatResponse(BaseModel):
    answer: str
    source_url: str | None
    platform_url: str | None
    last_updated: str | None
    fetch_timestamp: str | None
    is_refusal: bool
    intent: str                   # FACTUAL / COMPARISON / ADVICE / OUT_OF_SCOPE
    missing_data: bool = False
    fund_name: str | None = None  # populated for fund-specific answers; used by follow-up chips
```

### 9.3 Request Flow in `main.py`

```python
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # 1. Guardrail classify
    intent = classifier.classify(req.query)

    # 2. Short-circuit on advice/OOS
    if intent in ("ADVICE", "OUT_OF_SCOPE"):
        return refusal_response(intent)

    # 3. Entity extraction
    entities = extract_entities(req.query)

    # 4. Retrieve
    chunks = retriever.retrieve(
        query=req.query,
        country=req.country or entities.country,
        ticker=entities.ticker,
        section=entities.section,
    )

    # 5. Generate
    if not chunks:
        return missing_data_response()

    response = llm.generate(req.query, chunks)
    return response
```

---

## 10. Frontend Layer (`ui/`)

### 10.1 Streamlit Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  HealthcareRAG · Global Healthcare Funds Assistant              │
│  [Disclaimer banner — subtle, always visible]                   │
├──────────────┬──────────────────────────────────────────────────┤
│   SIDEBAR    │   MAIN CHAT AREA                                 │
│              │                                                  │
│  Country:    │   Welcome message (first load only)              │
│  [Dropdown]  │                                                  │
│              │   [Example question pills / buttons]             │
│  Fund:       │                                                  │
│  [Dropdown]  │   ─────── Chat history ───────                  │
│              │                                                  │
│  [About]     │   User: What is the expense ratio of XLV?        │
│              │                                                  │
│              │   Bot: The expense ratio of XLV is 0.09%.       │
│              │        Source: ssga.com/...                      │
│              │        Last updated from sources: 2026-05-15     │
│              │                                                  │
│              │   [Chat input box]         [Send button]         │
└──────────────┴──────────────────────────────────────────────────┘
```

### 10.2 Country Dropdown Options

```
All Countries
India
USA
Canada
China / Hong Kong
Japan
Singapore
UK / Europe
```

### 10.3 Source Card Display (per answer)

```
┌─────────────────────────────────────────────────────┐
│ Source  [Official] ssga.com/...                     │
│ Also see: etf.com/XLV                               │
│ Last updated from sources: 2026-05-15               │
│ Fetched by bot: 2026-06-02 10:00 AM IST             │
└─────────────────────────────────────────────────────┘
```

### 10.4 Welcome Message

```
Ask factual questions about healthcare, pharma, biotech, and med-tech funds
across India, USA, Canada, China, Hong Kong, Singapore, Japan, and the UK.

Facts only. No investment advice.
```

### 10.5 Example Questions (clickable pills)

```
What is the expense ratio of HDFC Pharma and Healthcare Fund?
Which healthcare funds are available in Canada?
What benchmark does XLV track?
Which funds in this corpus are biotech-focused?
Show healthcare funds country-wise.
What is the investment objective of VHT?
Who manages Nippon India Pharma Fund?
```

Clicking a pill auto-fills the chat input.

---

## 11. Scheduler (GitHub Actions)

Daily ingestion runs as a **GitHub Actions cron job**, not inside the FastAPI process. APScheduler has been removed. The Railway backend is a pure web server.

**Workflow file:** `.github/workflows/daily-ingestion.yml`

```yaml
on:
  schedule:
    - cron: "30 4 * * *"    # 4:30 AM UTC = 10:00 AM IST
  workflow_dispatch:         # also triggerable manually
```

On each run:
1. GitHub spins up an `ubuntu-latest` runner.
2. Installs dependencies + Playwright Chromium.
3. Runs `python -m ingestion.run_ingestion`:
   - Re-fetches all 34 active fund URLs in `sources.yaml`.
   - Tries `backup_platform_urls` when primary sources miss important fields.
   - Normalizes, chunks, embeds (BGE-large, 1024-dim).
   - Upserts into Qdrant Cloud (upsert by deterministic UUID, overwrites stale points).
4. Commits updated `data/parsed/**/*.json` back to `main` with `[skip ci]`.

**`scheduler/refresh.py`** is now a thin wrapper exposing `run_daily_refresh()` for the optional admin HTTP endpoint — no APScheduler dependency.

---

## 12. Data Flow — End-to-End

### 12.1 Ingestion (offline / scheduled)

```
sources.yaml
    → crawler.py          [HTTP GET / Playwright]
    → html_parser.py      [extract fields → try backup_platform_urls if fields missing]
    → pdf_parser.py       [for PDF sources]
    → normalizer.py       [map to normalized fields; merge official > pdf > platform > backups]
    → parsed_store.py     [save data/parsed/{country}/{fund_id}.json]
    → chunker.py          [split into section chunks]
    → embedder.py         [BGE encode — 1024-dim bge-large]
    → store.py            [Qdrant Cloud upsert]
    → logs/ingestion.log  [per-fund success / failure / missing fields]
```

### 12.2 Query (real-time)

```
User query
    → api/router.py       [POST /chat]
    │
    ├── PII check                          → PII refusal
    ├── fund list / total AUM              → structured YAML response
    ├── structured lookup (NEW)
    │       detect field keyword + fund    → read data/parsed JSON → instant answer
    ├── classify query
    │       ADVICE / OOS                   → refusal.py
    └── FACTUAL / COMPARISON
        → retriever.py    [Qdrant Cloud query with payload filter]
        → reranker.py     [boost official sources]
        → confidence gate [≥2 chunks with distance < 0.75]
        → prompt_builder.py
        → groq_client.py  [llama-3.3-70b-versatile]
        → response_formatter.py
        → ChatResponse    [answer + source + timestamp + fund_name]
    → Next.js frontend / Streamlit UI
```

---

## 13. Environment Variables (`.env.example`)

```env
# Groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_CLASSIFIER_MODEL=llama-3.1-8b-instant

# Embeddings
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# Qdrant Cloud
QDRANT_URL=https://your-cluster-id.us-east4-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION=healthcare_funds
# QDRANT_LOCAL_PATH=./vectorstore/qdrant_local  # dev fallback only

# Retrieval
TOP_K_RETRIEVAL=6

# Scheduler
SCHEDULER_HOUR_IST=10

# App
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8002
LOG_LEVEL=INFO
```

---

## 14. Ingestion Logging and Error Handling

Every ingestion run writes a structured log per fund:

```json
{
  "fund_id": "india_hdfc_pharma",
  "fetch_url": "https://groww.in/...",
  "fetch_status": "success",
  "fetch_timestamp": "2026-06-02T10:01:23+05:30",
  "fields_extracted": ["nav_or_price", "aum", "expense_ratio", "benchmark", "risk"],
  "fields_missing": ["top_10_holdings", "sector_exposure"],
  "chunks_upserted": 5,
  "parse_method": "playwright"
}
```

Error states:
| State | Handling |
|---|---|
| HTTP timeout / 4xx / 5xx | Mark source as `fetch_failed`; retain previous chunks; surface warning in UI |
| JS page empty after Playwright | Log warning; try official URL as fallback |
| PDF parse failure | Log warning; skip PDF chunks; HTML chunks still upserted |
| Zero chunks extracted | Log error; do NOT upsert; keep previous data |
| Chunk below min size | Discard silently; log count |

---

## 15. Key Architectural Decisions and Rationale

| Decision | Rationale |
|---|---|
| Semantic chunking by section (not fixed-size) | Enables metadata-filtered retrieval by field. Asking "what is the expense ratio?" retrieves only `cost_ratio` sections, not noise from holdings or objectives. |
| Metadata filter before semantic search | Prevents cross-country and cross-fund confusion. "What is the MER of HHL?" should not retrieve VHT's expense ratio. |
| BGE-large embedding model (bge-large-en-v1.5, 1024-dim) | Better retrieval quality than bge-small. Runs locally with no API cost. Privacy-safe. |
| Groq API for generation | Fast inference; llama-3.3-70b has strong instruction-following for structured outputs and refusals. |
| Two-stage guardrail (regex + LLM) | Regex catches high-confidence advice queries with zero LLM cost. LLM classifier handles edge cases only. |
| Structured lookup before RAG | For factual fund-field questions, read `data/parsed/{fund_id}.json` directly — no vector search, no LLM call, deterministic answer. |
| Upsert (not delete-all + reinsert) on refresh | Sources that fail on a given day retain their previous chunks. Bot stays functional even during partial refresh failures. |
| Official URL preferred for citations | Issuer pages are authoritative. Platform URLs may lag or restructure. |
| Backup platform URLs per fund | When primary/official sources fail to extract important fields, ordered fallback URLs are tried automatically during ingestion. |
| Normalization at ingestion time | Chunks stored with normalized labels. Retrieval and LLM prompts use one consistent vocabulary. No runtime translation. |
| Variable corpus size per country | Japan (4 funds) and Singapore (non-listed funds) are valid corpus states. System must not require exactly 5 funds per country. |
| Qdrant Cloud for vector store | Managed cloud Qdrant — no infrastructure to maintain. Free tier handles ~400 chunks at 1024-dim. Deterministic UUID5 IDs from chunk_id enable safe upsert. |
| GitHub Actions cron for daily ingestion | Cleanly separates serving from data refresh. Railway runs as a pure stateless web server. Ingestion logs are visible in GitHub UI. Free tier allows ~900 min/month for a 30-min daily job. Manual re-runs and per-fund triggers available via `workflow_dispatch`. |
| Next.js 14 frontend on Vercel | Production-grade React frontend with TanStack Query, Zustand, and Motion.dev. Deployed separately from the Python backend. |

---

## 16. Phase-by-Phase Build Order

| Phase | Deliverable | Key Files |
|---|---|---|
| 0 | Project scaffold + config | `config/sources.yaml`, `config/settings.py`, `.env.example`, `requirements.txt` |
| 1 | Ingestion pipeline | `ingestion/crawler.py`, `html_parser.py`, `pdf_parser.py`, `normalizer.py`, `run_ingestion.py` |
| 2 | Chunking + embeddings | `ingestion/chunker.py`, `embeddings/embedder.py`, `embeddings/store.py`, `embeddings/schema.py` |
| 3 | Retrieval | `retrieval/retriever.py`, `retrieval/reranker.py` |
| 4 | LLM generation | `llm/groq_client.py`, `llm/prompt_builder.py`, `llm/response_formatter.py` |
| 5 | Guardrails | `guardrails/classifier.py`, `guardrails/refusal.py` |
| 6 | API + UI | `api/main.py`, `api/models.py`, `ui/app.py`, `ui/components/` |
| 7 | Scheduler | `scheduler/refresh.py` (wired into FastAPI lifespan) |

---

## 17. Port Assignments

| Service | Port |
|---|---|
| FastAPI backend | 8002 |
| Streamlit frontend | 8502 |

(Chosen to avoid conflict with DishAI on 8001/8501 and Wayfarer on existing ports.)

---

## 18. `requirements.txt` (Initial)

```
fastapi
uvicorn[standard]
streamlit
pydantic
pydantic-settings
python-dotenv
requests
beautifulsoup4
playwright
pdfplumber
pypdf
sentence-transformers
chromadb
groq
apscheduler
pytz
pyyaml
pytest
httpx
```

---

## 19. Testing Strategy

| Layer | Test Type | What to Test |
|---|---|---|
| `crawler.py` | Unit | Static fetch returns HTML; Playwright fallback triggers on empty content |
| `normalizer.py` | Unit | Each country's raw terms map to correct normalized field |
| `chunker.py` | Unit | Each section produces exactly one chunk; chunk text includes fund + section label prefix |
| `retriever.py` | Integration | Country filter returns only that country's chunks; ticker filter returns only that fund's chunks |
| `classifier.py` | Unit | Regex catches all 8 advice-query examples from problem statement; LLM classifier returns valid label |
| `api/main.py` | Integration | `/chat` with advice query returns refusal; factual query returns source URL |
| Corpus | E2E | After ingestion, each fund has ≥ 5 populated chunks in ChromaDB |

---

## 20. React / Next.js Portfolio Frontend

A production-grade portfolio frontend lives in `frontend/` and runs on **port 3000** alongside the existing Streamlit MVP (port 8502). Both consume the same FastAPI backend (port 8002).

### Stack
| Layer | Tool |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS + design token system |
| Components | shadcn/ui (Zinc base, CSS variables) |
| Tables | Custom TanStack-style comparison table |
| Charts | Recharts (sector/geo exposure donuts) |
| Icons | Lucide React |
| Animation | Motion.dev v11 (`import from "motion/react"`) |
| State | TanStack Query v5 + Zustand (comparison store) |
| Forms | React Hook Form + Zod |

### Routes
```
/                   Home — hero, example chips, query input
/research           Ask AI — chat + healthcare backdrop animation
/funds              Fund Explorer — grouped by country, lazy financial details
/funds/[fundId]     Fund Detail — full facts, holdings, exposure charts
/compare            Compare Funds — side-by-side table, CSV export
/sources            Sources & Evidence — corpus status, evidence drawer
/about              About / Methodology + full disclaimer
```

### New Backend Endpoint Added
`GET /funds/{fund_id}/details` — reads `data/parsed/{country_slug}/{fund_id}.json` and returns `FundDetails`. Enables Fund Detail and Compare pages to show financial fields (NAV, AUM, expense ratio, holdings) without firing LLM requests.

### Timestamp Display
All corpus timestamps (from IST scheduler) are shown converted to **PDT/PST** in the UI — pure JS conversion, no external timezone library.

### Healthcare Backdrop
`components/backdrop/HealthcareBackdrop.tsx` — SVG + Motion.dev fixed-position backdrop on the `/research` page. Four layers: ECG heartbeat scroll, floating molecular orbs, DNA double helix, financial ticker strip. All layers `opacity: 0.05–0.08`, `pointer-events: none`.

### Development
```bash
cd frontend && npm run dev   # port 3000
```
