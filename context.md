# FinanceBot — Global Healthcare Funds RAG Assistant: Detailed Context

---

## 1. Project Identity

| Field | Value |
|---|---|
| Project Name | Global Healthcare Funds RAG Assistant |
| Short Name | FinanceBot / Healthcare RAG |
| Type | Facts-only Retrieval-Augmented Generation (RAG) chatbot |
| Domain | Healthcare / Pharma / Biotech / Med-Tech / Healthcare Innovation |
| Scope | Global (8 markets) — India, USA, Canada, China, Hong Kong, Singapore, Japan, UK/Europe |
| Persona | Public-facing informational assistant; no investment advice |

---

## 2. Core Problem Being Solved

Retail investors who want to explore healthcare-related investment funds across countries face three structural gaps:

1. **Fragmentation** — Fund information lives across Groww (India), ETF.com (USA), TMX Money (Canada), HKEX (HK), Yahoo Finance (international), JustETF (EU/UK), and individual issuer sites. No single unified interface exists.
2. **Terminology mismatch** — Each market uses different vocabulary for the same concepts (e.g., "expense ratio" in India/USA vs "MER" in Canada vs "TER/ongoing charge" in Europe).
3. **LLM hallucination risk** — Fund-level facts (NAV, AUM, holdings, expense ratios) change frequently. General-purpose LLMs may serve stale or fabricated data without citing sources.

The bot solves all three by ingesting public fund pages, normalizing terminology, and answering only from retrieved corpus content with mandatory source citations.

---

## 3. What the Bot WILL Do

- Answer factual questions about specific funds (expense ratio, AUM, benchmark, NAV, holdings, objective, risk rating, fund manager, fund house, exchange, currency, distribution policy).
- Compare funds across countries using only corpus-derived facts.
- Filter by country or fund.
- Show source links with every answer.
- Show last-updated timestamps from the source.
- Handle missing fields gracefully (say "not found in corpus" rather than hallucinate).
- Normalize global terminology into consistent labels.

## 4. What the Bot WILL NOT Do

- Provide buy/sell/hold recommendations.
- Build or suggest portfolios.
- Predict returns or performance.
- Give timing advice ("good time to buy").
- Give personalized or risk-profile-based advice.
- Rank funds as "best" unless ranking is based on a factual field (e.g., AUM).
- Answer from LLM memory — every answer must cite corpus content.
- Accept, store, or process any PII (PAN, Aadhaar, account numbers, broker credentials, email, phone, bank details).

---

## 5. Fund Universe (Corpus)

### 5.1 India — 5 Funds (Groww Platform URLs)

| # | Fund Name | Platform URL |
|---|---|---|
| 1 | HDFC Pharma and Healthcare Fund Direct Growth | groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth |
| 2 | Nippon India Pharma Fund Direct Growth | groww.in/mutual-funds/nippon-india-pharma-fund-direct-growth |
| 3 | Mirae Asset Healthcare Fund Direct Growth | groww.in/mutual-funds/mirae-asset-healthcare-fund-direct-growth |
| 4 | SBI Healthcare Opportunities Fund Direct Growth | groww.in/mutual-funds/sbi-pharma-fund-direct-growth |
| 5 | ICICI Prudential Pharma Healthcare and Diagnostics Fund | groww.in/mutual-funds/icici-prudential-pharma-healthcare-and-diagnostics-...-fund-direct-growth |

Backup: Tata India Pharma and Healthcare Fund, UTI Healthcare Fund.

**Key note:** India funds are mutual funds (not ETFs), available on Groww's no-login public pages. Terms: NAV, AUM, expense ratio, exit load, SIP, lumpsum, riskometer, direct growth.

---

### 5.2 USA — 5 Funds (ETF.com + Issuer Pages)

| # | Fund | Ticker | Issuer |
|---|---|---|---|
| 1 | Health Care Select Sector SPDR ETF | XLV | State Street (SSGA) |
| 2 | Vanguard Health Care ETF | VHT | Vanguard |
| 3 | iShares Global Healthcare ETF | IXJ | BlackRock / iShares |
| 4 | iShares Biotechnology ETF | IBB | BlackRock / iShares |
| 5 | Fidelity MSCI Health Care Index ETF | FHLC | Fidelity |

Backup: VanEck Pharmaceutical ETF (PPH).

**Key note:** USA funds are ETFs. Two sources per fund — ETF.com platform URL and official issuer URL. Official URL preferred for citations. Terms: expense ratio, NAV, market price, net assets, prospectus, holdings.

---

### 5.3 Canada — 5 Funds (TMX Money + Issuer Pages)

| # | Fund | Ticker | Issuer |
|---|---|---|---|
| 1 | Harvest Healthcare Leaders Income ETF | HHL | Harvest Portfolios |
| 2 | iShares Global Healthcare Index ETF CAD-Hedged | XHC | BlackRock Canada |
| 3 | BMO Equal Weight US Health Care Index ETF | ZHU | BMO GAM |
| 4 | TD Global Healthcare Leaders Index ETF | TDOC | TD Asset Management |
| 5 | Global X Equal Weight Global Healthcare Index ETF | MEDX | Global X Canada |

Backup: Evolve Global Healthcare Enhanced Yield Fund (LIFE.TO).

**Key note:** Canada funds are ETFs listed on TSX. Terms: MER, management fee, Fund Facts document, risk rating, sales charge, redemption fee, ETF Facts. SEDAR+ is the regulatory filing portal.

---

### 5.4 China / Hong Kong — 5 Entries (Yahoo Finance, HKEX, Issuer Pages)

| # | Fund | Ticker | Issuer |
|---|---|---|---|
| 1 | Global X China Biotech ETF | 2820.HK | Global X HK |
| 2 | CSOP Hang Seng Biotech ETF | 3174.HK | CSOP Asset Mgmt |
| 3 | ChinaAMC Hang Seng Biotech ETF | 3069.HK | ChinaAMC HK |
| 4 | KraneShares MSCI All China Health Care ETF | KURE (US-listed) | KraneShares |
| 5 | Global X China Biotech ETF — HKEX Quote | 2820 (HKEX) | Global X HK |

**Key note:** Many China-focused healthcare ETFs are HK-listed. Labels must distinguish between HK-listed, China-focused, and US-listed with China exposure. KURE is US-listed but China-focused.

---

### 5.5 Japan — 4 Funds (Yahoo Finance + Issuer Pages)

| # | Fund | Ticker | Issuer |
|---|---|---|---|
| 1 | NEXT FUNDS TOPIX-17 Pharmaceutical ETF | 1621.T | Nomura / NEXT FUNDS |
| 2 | Global X Japan Bio & Med Tech ETF | 2639.T | Global X Japan |
| 3 | Global X HealthTech ETF | HEAL (TBD) | Global X Japan |
| 4 | Global X Genomics & Biotechnology ETF | GNOM (TBD) | Global X Japan |

**Key note:** Japan may have fewer than 5 clean healthcare ETFs. The system must allow variable corpus sizes per country. Some tickers are TBD — validate during source ingestion phase.

---

### 5.6 UK / Europe — 5 Funds (JustETF + Official Issuer Pages)

| # | Fund | ISIN | Issuer |
|---|---|---|---|
| 1 | iShares S&P 500 Health Care Sector UCITS ETF | IE00B43HR379 | BlackRock / iShares UK |
| 2 | iShares Healthcare Innovation UCITS ETF | IE00BYZK4776 | BlackRock / iShares UK |
| 3 | SPDR MSCI World Health Care UCITS ETF | IE00BYTRRB94 | State Street SPDR Europe |
| 4 | Xtrackers MSCI World Health Care UCITS ETF | IE00BM67HK77 | DWS Xtrackers |
| 5 | Invesco US Health Care Sector UCITS ETF | IE00B3WMTH43 | Invesco |

**Key note:** UK/Europe funds are UCITS-structured ETFs. Identified by ISIN, not just ticker. Terms: TER, ongoing charge, fund size, SRRI, distribution policy, replication method, UCITS. JustETF is the platform equivalent of ETF.com for Europe.

---

### 5.7 Singapore — 5 Entries (Fund Pages + Factsheets)

| # | Fund / Source | Type |
|---|---|---|
| 1 | Wellington Global Health Care Equity Fund | Actively managed fund |
| 2 | Amova Asia Healthcare Fund | Asia-focused fund |
| 3 | Amova Asia Healthcare Fund Factsheet PDF | PDF document source |
| 4 | Fidelity Funds Global Healthcare Fund Singapore | Global healthcare fund |
| 5 | SGX Healthcare Index | Index reference |

**Key note:** Singapore may not have enough locally listed healthcare ETFs. This section covers Singapore-accessible funds (available to SG investors), not Singapore-listed ETFs. Includes at least one PDF factsheet source (Amova), which requires PDF parsing.

---

## 6. Data Fields to Extract and Normalize

Every fund document should yield as many of these fields as available:

| Normalized Field | Description |
|---|---|
| `overview` | Short description of the fund |
| `country_or_market` | India / USA / Canada / HK / China / Japan / Singapore / UK-Europe |
| `fund_name` | Full official fund name |
| `ticker_or_identifier` | Ticker symbol or ISIN |
| `fund_type` | Mutual Fund / ETF / UCITS ETF / Fund of Funds |
| `domain_subcategory` | Pharma / Broad Healthcare / Biotech / Med-Tech / Healthcare Innovation |
| `nav_or_price` | Current NAV or market price |
| `aum` | Assets Under Management / Net Assets / Fund Size |
| `expense_ratio_or_mer_or_ter` | Cost ratio (normalized across terminologies) |
| `minimum_investment` | Minimum lumpsum or equivalent |
| `minimum_sip` | Minimum SIP (India-specific; N/A for ETFs) |
| `exit_load_or_redemption_fee` | Exit cost if any |
| `benchmark` | Index tracked or benchmarked against |
| `fund_management` | Portfolio manager or management team |
| `fund_house_or_issuer` | AMC / issuer / asset manager |
| `investment_objective` | Official investment objective statement |
| `risk_rating_or_riskometer` | Risk level (Low / Moderate / High / SRRI 1–7) |
| `holdings` | Full or partial holdings list |
| `top_10_holdings` | Top 10 constituent holdings |
| `sector_exposure` | Sector-level allocation breakdown |
| `geographic_exposure` | Country/regional allocation breakdown |
| `distribution_policy` | Accumulating / distributing / dividend |
| `currency` | Fund currency (INR / USD / CAD / HKD / JPY / GBP / EUR) |
| `exchange` | Listed exchange (NSE/BSE / NYSE/Nasdaq / TSX / HKEX / TSE / LSE) |
| `tax_information` | Tax notes if available in source |
| `documents` | Links to factsheets, prospectus, Fund Facts, ETF Facts |
| `platform_url` | Groww / ETF.com / TMX / Yahoo / HKEX / JustETF URL |
| `official_url` | Issuer / AMC / exchange official page |
| `last_updated_from_source` | Date visible in source page or document |
| `fetch_timestamp` | When the bot last fetched this URL |

---

## 7. Terminology Normalization Table

| Normalized Label | India | USA | Canada | UK / Europe |
|---|---|---|---|---|
| Cost ratio | Expense ratio | Expense ratio | MER / management fee | TER / ongoing charge |
| Risk | Riskometer | Risk level | Risk rating | SRRI / risk indicator |
| Price | NAV | NAV / market price | NAV / market price | NAV / market price |
| Fund size | AUM | Net assets / AUM | Net assets / AUM | Fund size |
| Exit cost | Exit load | Redemption fee / sales load | Sales charge / redemption fee | Entry/exit charge |
| Min investment | Min SIP / lumpsum | Investment minimum | Minimum investment | Minimum investment |
| Fund manager | Fund manager | Portfolio manager / advisor | Portfolio manager | Investment manager |
| Fund house | AMC | Issuer / adviser | Manager / issuer | Issuer / asset manager |

The RAG layer must normalize extracted text using this table before storing chunks, and must use normalized labels in responses.

---

## 8. Source Strategy

Two URL types per fund where possible:

| Type | Purpose | Use in Answers |
|---|---|---|
| Platform URL | User-facing discovery pages (Groww, ETF.com, TMX, JustETF, Yahoo Finance, HKEX) | Display / fallback |
| Official URL | Issuer/AMC/exchange/regulator/factsheet pages | Preferred for citations |

**Rule:** Prefer official URLs in all citations. Use platform URLs as fallback or for display context.

---

## 9. RAG Answer Rules (Hard Constraints)

1. Answer ONLY from retrieved corpus chunks — never from LLM memory.
2. Every factual answer must include at least one source link.
3. Answers must be concise.
4. No investment advice in any form.
5. No return computation or prediction.
6. No "best fund" ranking unless based on an explicit factual field in the corpus (e.g., "largest AUM").
7. If data is missing, respond: *"I could not find this information in the current source set."*
8. Include `last_updated_from_source` where available.
9. Prefer official URLs for citations.
10. Use platform URLs for display/fallback only.

---

## 10. Refusal Logic

Trigger a refusal when the user asks:
- Whether to buy/sell/hold a fund.
- Which fund is "best" or "better."
- For portfolio construction or allocation.
- For return predictions or performance expectations.
- For risk-profile-based recommendations.
- For tax planning advice.
- For timing advice ("right time to buy").

**Refusal template:**
> I can't provide investment advice or buy/sell recommendations. I can help with factual details such as expense ratio, AUM, benchmark, holdings, risk rating, investment objective, and official source documents.

Refusal must be polite, concise, non-judgmental, and must offer a factual alternative question the user could ask instead.

---

## 11. System Architecture (Phases)

### Phase 0 — Project Setup
- Directory structure, environment files (.env), source list JSON/YAML, documentation (context.md, README).

### Phase 1 — Ingestion and Parsing
- Fetch each corpus URL.
- Handle HTML pages (BeautifulSoup / Playwright for JS-heavy pages).
- Handle PDF documents (pypdf / pdfplumber for Singapore Amova factsheet and similar).
- Save raw content.
- Extract fund-specific text sections.
- Store cleaned text per fund.

### Phase 2 — Chunking and Embeddings
- Chunk by semantic section: overview, expense ratio / MER / TER, benchmark, holdings, objective, risk, documents.
- Attach metadata per chunk: `country`, `fund_name`, `ticker`, `domain_subcategory`, `source_type` (platform / official), `source_url`, `fetch_timestamp`.
- Embedding model: BGE small / base / large (open-source, choose based on resource constraints).
- Vector store: ChromaDB or FAISS (local), or Pinecone / Qdrant (cloud option).

### Phase 3 — Retrieval
- Metadata-aware retrieval with filters: `country`, `fund_name`, `ticker`, `domain_subcategory`, `source_type`.
- Hybrid retrieval: semantic similarity + metadata filter.
- Prefer official-source chunks in ranking.

### Phase 4 — LLM Response Generation
- LLM: Groq (primary, consistent with DishAI and Wayfarer projects) — e.g., llama-3.3-70b-versatile or gemma2-9b-it.
- Prompt includes: retrieved chunks + metadata + normalization rules + hard constraints (facts-only, cite source, refuse advice).
- Output format: answer + source URL + last_updated_from_source.

### Phase 5 — Guardrails
- Classify user query before retrieval: factual | comparison | advice-seeking | out-of-scope.
- Advice-seeking and out-of-scope queries hit the refusal handler before retrieval runs.
- Guardrail can use a lightweight LLM call or keyword/regex classifier.

### Phase 6 — UI
- Framework: Streamlit (consistent with other projects in this workspace).
- UI elements:
  - Welcome banner with domain note.
  - Facts-only disclaimer.
  - Country filter (dropdown: All / India / USA / Canada / China-HK / Japan / Singapore / UK-Europe).
  - Fund filter (optional, dependent on country selection).
  - Example questions panel.
  - Chat input.
  - Answer display with source link and last_updated_from_source.
  - Clear refusal message area.

### Phase 7 — Scheduler
- Daily refresh at **10:00 AM IST**.
- Re-fetch all corpus URLs.
- Re-extract, re-chunk, re-embed updated content.
- Log fetch timestamps.
- Tool: APScheduler / cron / Celery beat.

---

## 12. UI Spec

### Welcome Line
> Ask factual questions about healthcare, pharma, biotech, and med-tech funds across India, USA, Canada, China, Hong Kong, Singapore, Japan, and the UK. Facts only. No investment advice.

### Example Questions (shown in UI)
```
What is the expense ratio of HDFC Pharma and Healthcare Fund?
Which healthcare funds are available in Canada?
What benchmark does XLV track?
Which funds in this corpus are biotech-focused?
Show healthcare funds country-wise.
```

### Disclaimer
> This assistant provides factual information from public sources only. It does not provide investment advice, buy/sell recommendations, portfolio allocation, return predictions, or personalized financial guidance. Always verify details from official fund documents before making financial decisions.

### Answer Format

**Factual answer:**
```
[Concise factual answer]

Source: [official_url or platform_url]
Last updated from sources: [date or fetch_timestamp]
```

**Comparison answer:**
```
[Side-by-side or listed factual comparison]

Sources: [url1], [url2]
Last updated from sources: [dates]
```

**Refusal:**
```
I can't recommend whether you should buy or sell a fund. I can help with factual details such as expense ratio, AUM, benchmark, holdings, risk rating, and investment objective from public sources.
```

**Missing data:**
```
I could not find this information in the current source set for this fund.
```

---

## 13. Security and Privacy Constraints

- Public sources only — no login, no OTP, no PAN/Aadhaar, no portfolio data.
- System must not accept, request, or store: PAN, Aadhaar, account numbers, OTP, email, phone, broker credentials, demat details, bank details, portfolio screenshots.
- No financial advice of any kind.
- No unsupported claims — all facts must be grounded in retrieved content.

---

## 14. Known Technical Risks

| Risk | Impact | Mitigation |
|---|---|---|
| JS-heavy pages (Groww, some issuer pages) | Scraper returns empty/partial content | Use Playwright for JS-rendered pages; fall back to issuer's official PDF/factsheet |
| Pages blocking automated scraping | Ingestion failure for that fund | Rotate user-agent; use respectful rate limiting; mark source as unavailable and surface warning in UI |
| Page structure changes | Extraction breaks | Monitor field-level extraction success rates; alert on drop |
| Fewer than 5 funds in a market (Japan, Singapore) | Thinner corpus | Allow variable corpus size per country; clearly label scope in UI |
| Currency heterogeneity | Confusing comparisons | Out of scope for v1 — state currency per fund, do not convert |
| Stale data | Wrong facts served | Daily refresh scheduler; show fetch_timestamp prominently |
| PDF-only sources (Singapore/Amova factsheet) | Requires PDF parsing pipeline | Use pdfplumber or pypdf in Phase 1 |

---

## 15. Success Criteria

| Criterion | Validation |
|---|---|
| Ingests all corpus URLs | All platform + official URLs return content |
| Extracts and chunks fund facts | Each fund has ≥ 5 populated normalized fields |
| Answers factual questions with citations | Source URL present in every answer |
| Refuses advice questions | Refusal fires for all out-of-scope query types |
| Country-wise comparison works | Filter by country returns correct fund subset |
| Missing fields handled gracefully | "Not found in corpus" instead of hallucination |
| Simple UI with example questions and disclaimer | All 9 required UI elements present |
| Source transparency | last_updated_from_source shown per answer |
| Daily refresh scheduler works | Fetch timestamps update daily at 10:00 AM IST |
| Extensible architecture | Adding a new country or domain requires only corpus + source list changes |

---

## 16. Future Extension Points

- Additional countries: Australia, Germany, South Korea, Taiwan.
- Additional sectors: AI funds, clean energy, defense, semiconductors, fintech, infrastructure.
- Currency conversion layer (v2).
- Performance comparison if return data is available in corpus (v2).
- PDF factsheet ingestion improvement (better table extraction).
- Multi-language support for non-English fund pages (Japan, China).

---

## 17. Corpus Source Summary Table

| Country | Platform | Official Sources | Fund Type | # Funds |
|---|---|---|---|---|
| India | Groww | HDFC AMC, Nippon, Mirae, SBI, ICICI Pru | Mutual Fund | 5 |
| USA | ETF.com | SSGA, Vanguard, BlackRock, Fidelity | ETF | 5 |
| Canada | TMX Money | Harvest, BlackRock CA, BMO, TD AM, Global X CA | ETF | 5 |
| China / HK | Yahoo, HKEX | Global X HK, CSOP, ChinaAMC, KraneShares | ETF | 5 |
| Japan | Yahoo Finance | NEXT FUNDS, Global X Japan | ETF | 4 |
| UK / Europe | JustETF | iShares UK, SSGA Europe, DWS, Invesco | UCITS ETF | 5 |
| Singapore | Issuer pages | Wellington, Amova (incl. PDF), Fidelity SG, SGX | Fund / Index | 5 |

**Total corpus entries: ~34 fund-level sources** (platform + official = up to 68 URLs).

---

## 18. Technology Stack (Recommended)

| Layer | Tool |
|---|---|
| Scraping (static) | requests + BeautifulSoup |
| Scraping (JS-heavy) | Playwright |
| PDF parsing | pdfplumber or pypdf |
| Embedding model | BGE-small-en-v1.5 (start) → BGE-base or large if needed |
| Vector store | ChromaDB (local dev) / Qdrant or Pinecone (production) |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Backend | FastAPI |
| Frontend | Streamlit |
| Scheduler | APScheduler (in-process) or cron |
| Environment | Python 3.11+, .env via python-dotenv |

---

## 19. Key Design Decisions

1. **Facts-only, no advice** — This is a hard constraint baked into prompt templates and a pre-retrieval guardrail classifier.
2. **Two-URL strategy per fund** — Platform URLs for user-facing display; official URLs for citations. Ingestion should fetch both.
3. **Metadata-tagged chunks** — Every chunk stores `country`, `fund`, `ticker`, `source_type`, and `source_url` so retrieval can filter by country/fund before semantic ranking.
4. **Variable corpus size per country** — Japan and Singapore may have fewer funds; the system must not error or pad with irrelevant funds.
5. **Graceful missing field handling** — Never hallucinate missing fields; always say "not found in corpus."
6. **Scheduled daily refresh at 10:00 AM IST** — Keeps NAV, AUM, and expense ratio data fresh.
7. **Normalization at ingestion time** — Country-specific terms are mapped to normalized field names when chunks are stored, not at query time.

---

## Portfolio Frontend (Next.js)

A production-grade React frontend was built in `frontend/` following the full design system in `design.md`.

- **Port:** 3000 (Streamlit MVP stays on 8502)
- **Start:** `cd frontend && npm run dev`
- **Build:** `cd frontend && npm run build`
- **New API endpoint:** `GET /funds/{fund_id}/details` reads `data/parsed/{slug}/{fund_id}.json`
- **Timestamp display:** IST corpus timestamps shown in PDT/PST in the UI
- **Backdrop:** Healthcare-themed SVG animation (ECG, molecular orbs, DNA helix, ticker) on `/research` page
