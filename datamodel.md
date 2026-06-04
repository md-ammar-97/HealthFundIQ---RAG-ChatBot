# FinanceBot — Global Healthcare Funds RAG Assistant: Data Model

---

## 0. Model Map

The system uses six discrete data models, each scoped to a single pipeline stage. Data flows linearly from ingestion through to the API response — no model is mutated after it leaves its stage.

```
sources.yaml (FundSource)
        │
        ▼
  [crawler.py]
        │
        ▼
  RawFetch          ← HTML / PDF bytes + fetch metadata
        │
        ▼
  ParsedFund        ← country-specific raw field labels + extracted text
        │
        ▼
  NormalizedFund    ← all fields use canonical normalized keys
        │
        ▼
  Chunk             ← one per section; carries full retrieval metadata
        │ (stored in ChromaDB)
        ▼
  BotResponse       ← LLM answer + source URL + timestamp
        │ (returned by FastAPI)
        ▼
  ChatResponse      ← Pydantic API response model for Streamlit
```

---

## 1. FundSource — `config/sources.yaml`

The corpus registry. One entry per fund. This is the only place fund identity and URLs are declared.

### 1.1 YAML Schema

```yaml
funds:
  - id: string                    # REQUIRED. Snake-case unique key: <country>_<short_name>
    country: string               # REQUIRED. One of: India | USA | Canada | China/HK | Japan | Singapore | UK/Europe
    fund_name: string             # REQUIRED. Full official fund name
    ticker: string | null         # Ticker symbol (null for India mutual funds and some Singapore funds)
    isin: string | null           # 12-char ISIN (required for UK/Europe UCITS ETFs; null otherwise)
    fund_type: string             # REQUIRED. One of: Mutual Fund | ETF | UCITS ETF | Fund | Index
    domain_subcategory: string    # REQUIRED. One of: Pharma | Broad Healthcare | Biotech | Med-Tech | Healthcare Innovation | Index
    currency: string              # REQUIRED. ISO 4217 code: INR | USD | CAD | HKD | JPY | GBP | EUR
    exchange: string | null       # Primary listing exchange (null for OTC / unlisted funds)
    platform_url: string          # REQUIRED. Public no-login platform page URL
    official_url: string | null   # Issuer / AMC / regulator page (preferred for citations)
    official_url_validated: bool  # false until Phase 1 confirms URL is live and content-rich
    use_playwright: bool          # true if JS rendering required for platform_url
    official_use_playwright: bool # true if JS rendering required for official_url
    has_pdf: bool                 # true if a PDF factsheet URL exists for this fund
    pdf_url: string | null        # Direct URL to downloadable PDF factsheet
    is_backup: bool               # true = backup fund; false = primary corpus fund
    backup_platform_urls: list[string] | null  # Ordered fallback URLs tried when primary parse leaves important fields missing
```

### 1.2 Full `sources.yaml` Content

```yaml
funds:

  # ─── INDIA ────────────────────────────────────────────────────────────────
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
    official_url: null
    official_url_validated: false
    use_playwright: true
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: india_nippon_pharma
    country: India
    fund_name: Nippon India Pharma Fund Direct Growth
    ticker: null
    isin: null
    fund_type: Mutual Fund
    domain_subcategory: Pharma
    currency: INR
    exchange: BSE / NSE
    platform_url: https://groww.in/mutual-funds/nippon-india-pharma-fund-direct-growth
    official_url: null
    official_url_validated: false
    use_playwright: true
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: india_mirae_healthcare
    country: India
    fund_name: Mirae Asset Healthcare Fund Direct Growth
    ticker: null
    isin: null
    fund_type: Mutual Fund
    domain_subcategory: Broad Healthcare
    currency: INR
    exchange: BSE / NSE
    platform_url: https://groww.in/mutual-funds/mirae-asset-healthcare-fund-direct-growth
    official_url: null
    official_url_validated: false
    use_playwright: true
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: india_sbi_healthcare
    country: India
    fund_name: SBI Healthcare Opportunities Fund Direct Growth
    ticker: null
    isin: null
    fund_type: Mutual Fund
    domain_subcategory: Broad Healthcare
    currency: INR
    exchange: BSE / NSE
    platform_url: https://groww.in/mutual-funds/sbi-pharma-fund-direct-growth
    official_url: null
    official_url_validated: false
    use_playwright: true
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: india_icici_phd
    country: India
    fund_name: ICICI Prudential Pharma Healthcare and Diagnostics Fund Direct Growth
    ticker: null
    isin: null
    fund_type: Mutual Fund
    domain_subcategory: Pharma / Broad Healthcare
    currency: INR
    exchange: BSE / NSE
    platform_url: https://groww.in/mutual-funds/icici-prudential-pharma-healthcare-and-diagnostics-%28p.h.d%29-fund-direct-growth
    official_url: null
    official_url_validated: false
    use_playwright: true
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: india_tata_pharma
    country: India
    fund_name: Tata India Pharma and Healthcare Fund Direct Growth
    ticker: null
    isin: null
    fund_type: Mutual Fund
    domain_subcategory: Pharma / Broad Healthcare
    currency: INR
    exchange: BSE / NSE
    platform_url: https://groww.in/mutual-funds/tata-india-pharma-and-healthcare-fund-direct-growth
    official_url: null
    official_url_validated: false
    use_playwright: true
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: true

  - id: india_uti_healthcare
    country: India
    fund_name: UTI Healthcare Fund Direct Growth
    ticker: null
    isin: null
    fund_type: Mutual Fund
    domain_subcategory: Broad Healthcare
    currency: INR
    exchange: BSE / NSE
    platform_url: https://groww.in/mutual-funds/uti-pharma-and-healthcare-fund-direct-growth
    official_url: null
    official_url_validated: false
    use_playwright: true
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: true

  # ─── USA ──────────────────────────────────────────────────────────────────
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

  - id: usa_vht
    country: USA
    fund_name: Vanguard Health Care ETF
    ticker: VHT
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: NYSE Arca
    platform_url: https://www.etf.com/VHT
    official_url: https://investor.vanguard.com/investment-products/etfs/profile/vht
    official_url_validated: true
    use_playwright: false
    official_use_playwright: true
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: usa_ixj
    country: USA
    fund_name: iShares Global Healthcare ETF
    ticker: IXJ
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: NYSE Arca
    platform_url: https://www.etf.com/IXJ
    official_url: https://www.ishares.com/us/products/239744/ishares-global-healthcare-etf
    official_url_validated: true
    use_playwright: false
    official_use_playwright: true
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: usa_ibb
    country: USA
    fund_name: iShares Biotechnology ETF
    ticker: IBB
    isin: null
    fund_type: ETF
    domain_subcategory: Biotech
    currency: USD
    exchange: Nasdaq
    platform_url: https://www.etf.com/IBB
    official_url: https://www.ishares.com/us/products/239699/ishares-biotechnology-etf
    official_url_validated: true
    use_playwright: false
    official_use_playwright: true
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: usa_fhlc
    country: USA
    fund_name: Fidelity MSCI Health Care Index ETF
    ticker: FHLC
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: NYSE Arca
    platform_url: https://www.etf.com/FHLC
    official_url: https://digital.fidelity.com/prgw/digital/research/quote/dashboard/summary?symbol=FHLC
    official_url_validated: true
    use_playwright: false
    official_use_playwright: true
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: usa_pph
    country: USA
    fund_name: VanEck Pharmaceutical ETF
    ticker: PPH
    isin: null
    fund_type: ETF
    domain_subcategory: Pharma
    currency: USD
    exchange: Nasdaq
    platform_url: https://www.etf.com/PPH
    official_url: https://www.vaneck.com/us/en/investments/pharmaceutical-etf-pph/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: true

  # ─── CANADA ───────────────────────────────────────────────────────────────
  - id: canada_hhl
    country: Canada
    fund_name: Harvest Healthcare Leaders Income ETF
    ticker: HHL
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: CAD
    exchange: TSX
    platform_url: https://money.tmx.com/en/quote/HHL
    official_url: https://harvestportfolios.com/etf/hhl/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: canada_xhc
    country: Canada
    fund_name: iShares Global Healthcare Index ETF CAD-Hedged
    ticker: XHC
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: CAD
    exchange: TSX
    platform_url: https://money.tmx.com/en/quote/XHC
    official_url: https://www.blackrock.com/ca/investors/en/products/239743/ishares-global-healthcare-index-etf-cadhedged-fund
    official_url_validated: true
    use_playwright: false
    official_use_playwright: true
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: canada_zhu
    country: Canada
    fund_name: BMO Equal Weight US Health Care Index ETF
    ticker: ZHU
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: CAD
    exchange: TSX
    platform_url: https://money.tmx.com/en/quote/ZHU
    official_url: https://bmogam.com/ca-en/products/exchange-traded-fund/bmo-equal-weight-us-health-care-index-etf-zhu/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: canada_tdoc
    country: Canada
    fund_name: TD Global Healthcare Leaders Index ETF
    ticker: TDOC
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: CAD
    exchange: TSX
    platform_url: https://money.tmx.com/en/quote/TDOC
    official_url: https://www.td.com/ca/en/asset-management/funds/solutions/etfs/fundcard?fundId=7192&fundname=TD-Global-Healthcare-Leaders-Index-ETF
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: canada_medx
    country: Canada
    fund_name: Global X Equal Weight Global Healthcare Index ETF
    ticker: MEDX
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: CAD
    exchange: TSX
    platform_url: https://money.tmx.com/en/quote/MEDX
    official_url: https://www.globalx.ca/product/medx
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: canada_life
    country: Canada
    fund_name: Evolve Global Healthcare Enhanced Yield Fund
    ticker: LIFE
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: CAD
    exchange: TSX
    platform_url: https://finance.yahoo.com/quote/LIFE.TO/
    official_url: https://evolveetfs.com/product/life/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: true

  # ─── CHINA / HONG KONG ────────────────────────────────────────────────────
  - id: hk_2820_yahoo
    country: China/HK
    fund_name: Global X China Biotech ETF
    ticker: "2820.HK"
    isin: null
    fund_type: ETF
    domain_subcategory: Biotech
    currency: HKD
    exchange: HKEX
    platform_url: https://finance.yahoo.com/quote/2820.HK/
    official_url: https://www.globalxetfs.com.hk/funds/china-biotech-etf/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: hk_3174
    country: China/HK
    fund_name: CSOP Hang Seng Biotech ETF
    ticker: "3174.HK"
    isin: null
    fund_type: ETF
    domain_subcategory: Biotech
    currency: HKD
    exchange: HKEX
    platform_url: https://sg.finance.yahoo.com/quote/3174.HK/
    official_url: https://www.csopasset.com/en/products/hk-health
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: hk_3069
    country: China/HK
    fund_name: ChinaAMC Hang Seng Biotech ETF
    ticker: "3069.HK"
    isin: null
    fund_type: ETF
    domain_subcategory: Biotech
    currency: HKD
    exchange: HKEX
    platform_url: https://finance.yahoo.com/quote/3069.HK/
    official_url: https://www.chinaamc.com.hk/product/chinaamc-hang-seng-hong-kong-biotech-index-etf-3069-hk-9069-hk/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: us_kure
    country: China/HK
    fund_name: KraneShares MSCI All China Health Care Index ETF
    ticker: KURE
    isin: null
    fund_type: ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: NYSE Arca
    platform_url: https://finance.yahoo.com/quote/KURE/
    official_url: https://kraneshares.com/etf/kure/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: hk_2820_hkex
    country: China/HK
    fund_name: Global X China Biotech ETF (HKEX Quote)
    ticker: "2820"
    isin: null
    fund_type: ETF
    domain_subcategory: Biotech
    currency: HKD
    exchange: HKEX
    platform_url: https://www.hkex.com.hk/Market-Data/Securities-Prices/Exchange-Traded-Products/Exchange-Traded-Products-Quote?sc_lang=en&sym=2820
    official_url: https://www.globalxetfs.com.hk/funds/china-biotech-etf/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  # ─── JAPAN ────────────────────────────────────────────────────────────────
  - id: jp_1621
    country: Japan
    fund_name: NEXT FUNDS TOPIX-17 Pharmaceutical ETF
    ticker: "1621.T"
    isin: null
    fund_type: ETF
    domain_subcategory: Pharma
    currency: JPY
    exchange: TSE
    platform_url: https://finance.yahoo.com/quote/1621.T/
    official_url: https://nextfunds.jp/en/lineup/1621/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: jp_2639
    country: Japan
    fund_name: Global X Japan Bio & Med Tech ETF
    ticker: "2639.T"
    isin: null
    fund_type: ETF
    domain_subcategory: Biotech / Med-Tech
    currency: JPY
    exchange: TSE
    platform_url: https://finance.yahoo.com/quote/2639.T/
    official_url: https://globalxetfs.co.jp/en/funds/2639/index.html
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: jp_heal
    country: Japan
    fund_name: Global X HealthTech ETF
    ticker: null
    isin: null
    fund_type: ETF
    domain_subcategory: Med-Tech / Healthcare Innovation
    currency: JPY
    exchange: TSE
    platform_url: https://globalxetfs.co.jp/en/funds/heal/
    official_url: https://globalxetfs.co.jp/en/funds/heal/
    official_url_validated: false
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: jp_gnom
    country: Japan
    fund_name: Global X Genomics & Biotechnology ETF
    ticker: null
    isin: null
    fund_type: ETF
    domain_subcategory: Biotech
    currency: JPY
    exchange: TSE
    platform_url: https://globalxetfs.co.jp/en/funds/gnom/
    official_url: https://globalxetfs.co.jp/en/funds/gnom/
    official_url_validated: false
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  # ─── UK / EUROPE ──────────────────────────────────────────────────────────
  - id: uk_ie00b43hr379
    country: UK/Europe
    fund_name: iShares S&P 500 Health Care Sector UCITS ETF
    ticker: null
    isin: IE00B43HR379
    fund_type: UCITS ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: LSE
    platform_url: https://www.justetf.com/en/etf-profile.html?isin=IE00B43HR379
    official_url: https://www.ishares.com/uk/individual/en/products/280507/ishares-sp-500-health-care-sector-ucits-etf
    official_url_validated: true
    use_playwright: false
    official_use_playwright: true
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: uk_ie00byzk4776
    country: UK/Europe
    fund_name: iShares Healthcare Innovation UCITS ETF
    ticker: null
    isin: IE00BYZK4776
    fund_type: UCITS ETF
    domain_subcategory: Healthcare Innovation
    currency: USD
    exchange: LSE
    platform_url: https://www.justetf.com/en/etf-profile.html?isin=IE00BYZK4776
    official_url: https://www.ishares.com/uk/individual/en/products/284216/ishares-healthcare-innovation-ucits-etf
    official_url_validated: true
    use_playwright: false
    official_use_playwright: true
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: uk_ie00bytrrb94
    country: UK/Europe
    fund_name: SPDR MSCI World Health Care UCITS ETF
    ticker: null
    isin: IE00BYTRRB94
    fund_type: UCITS ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: LSE
    platform_url: https://www.justetf.com/en/etf-profile.html?isin=IE00BYTRRB94
    official_url: https://www.ssga.com/nl/en_gb/intermediary/etfs/state-street-spdr-msci-world-health-care-ucits-etf-whea-na
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: uk_ie00bm67hk77
    country: UK/Europe
    fund_name: Xtrackers MSCI World Health Care UCITS ETF
    ticker: null
    isin: IE00BM67HK77
    fund_type: UCITS ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: LSE
    platform_url: https://www.justetf.com/en/etf-profile.html?isin=IE00BM67HK77
    official_url: https://etf.dws.com/en-ch/IE00BM67HK77-msci-world-health-care-ucits-etf-1c/
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: uk_ie00b3wmth43
    country: UK/Europe
    fund_name: Invesco US Health Care Sector UCITS ETF
    ticker: null
    isin: IE00B3WMTH43
    fund_type: UCITS ETF
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: LSE
    platform_url: https://www.justetf.com/en/etf-profile.html?isin=IE00B3WMTH43
    official_url: null
    official_url_validated: false
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  # ─── SINGAPORE ────────────────────────────────────────────────────────────
  - id: sg_wellington
    country: Singapore
    fund_name: Wellington Global Health Care Equity Fund
    ticker: null
    isin: null
    fund_type: Fund
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: null
    platform_url: https://www.wellington.com/en-sg/intermediary/funds/global-health-care-equity-fund
    official_url: https://www.wellington.com/en-sg/intermediary/funds/global-health-care-equity-fund
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: sg_amova
    country: Singapore
    fund_name: Amova Asia Healthcare Fund
    ticker: null
    isin: null
    fund_type: Fund
    domain_subcategory: Broad Healthcare
    currency: JPY
    exchange: null
    platform_url: https://sg.amova-am.com/general/funds/detail/amova-asia-healthcare-fund-jpy-class
    official_url: https://sg.amova-am.com/general/funds/detail/amova-asia-healthcare-fund-jpy-class
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: true
    pdf_url: https://sg.amova-am.com/docs/default-source/sg-library/fund/factsheet/AMOVA-ASIA-HEALTHCARE-FUND-FACTSHEET.pdf
    is_backup: false

  - id: sg_fidelity
    country: Singapore
    fund_name: Fidelity Funds Global Healthcare Fund Singapore
    ticker: null
    isin: null
    fund_type: Fund
    domain_subcategory: Broad Healthcare
    currency: USD
    exchange: null
    platform_url: https://www.fidelity.com.sg/investment/equity/global-healthcare
    official_url: https://www.fidelity.com.sg/investment/equity/global-healthcare
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false

  - id: sg_sgx_index
    country: Singapore
    fund_name: SGX Healthcare Index
    ticker: null
    isin: null
    fund_type: Index
    domain_subcategory: Broad Healthcare
    currency: SGD
    exchange: SGX
    platform_url: https://www.sgx.com/indices/products/sgxhc
    official_url: https://www.sgx.com/indices/products/sgxhc
    official_url_validated: true
    use_playwright: false
    official_use_playwright: false
    has_pdf: false
    pdf_url: null
    is_backup: false
```

---

## 2. RawFetch — `ingestion/crawler.py` output

Produced immediately after the HTTP/Playwright fetch. Stored in `data/raw/<country>/<fund_id>/`.

### 2.1 Python Dataclass

```python
from dataclasses import dataclass, field

@dataclass
class RawFetch:
    fund_id: str                  # matches FundSource.id
    url: str                      # the URL that was fetched
    source_type: str              # "platform" or "official" or "pdf"
    content_type: str             # "html" or "pdf"
    raw_content: str | bytes      # str for HTML; bytes for PDF
    fetch_timestamp: str          # ISO 8601 with timezone: "2026-06-02T10:01:23+05:30"
    http_status: int              # HTTP status code returned
    fetch_method: str             # "requests" or "playwright"
    content_length: int           # len(raw_content) in bytes / chars
    fetch_success: bool           # False if HTTP error, timeout, or content < MIN_SIZE
    error_message: str | None     # error text if fetch_success is False
```

### 2.2 File Storage

```
data/raw/
  india/
    india_hdfc_pharma/
      platform_page.html          # from Groww URL
      official_page.html          # from AMC URL (if available)
  usa/
    usa_xlv/
      platform_page.html          # from etf.com/XLV
      official_page.html          # from ssga.com
  singapore/
    sg_amova/
      platform_page.html
      factsheet.pdf               # from pdf_url
```

### 2.3 Validation Rules

| Field | Rule |
|---|---|
| `http_status` | Must be 200; 4xx/5xx sets `fetch_success = False` |
| `content_length` | HTML: min 500 chars; PDF: min 1000 bytes; below → retry with Playwright or mark failed |
| `fetch_timestamp` | Always UTC+5:30 (IST), ISO 8601 format |
| `source_type` | Must be one of: `platform`, `official`, `pdf` |

---

## 3. ParsedFund — `ingestion/html_parser.py` + `pdf_parser.py` output

Produced after extracting text fields from the raw HTML or PDF. Field keys use country-specific terminology at this stage — normalization happens in the next step.

### 3.1 Python Dataclass

```python
from dataclasses import dataclass, field

@dataclass
class ParsedFund:
    fund_id: str                      # matches FundSource.id
    country: str                      # from FundSource.country
    fund_name: str                    # from FundSource.fund_name
    ticker: str | None                # from FundSource.ticker
    isin: str | None                  # from FundSource.isin
    source_url: str                   # the URL parsed
    source_type: str                  # "platform" or "official" or "pdf"
    fetch_timestamp: str              # ISO 8601 — carried forward from RawFetch
    parse_method: str                 # "beautifulsoup" or "playwright" or "pdfplumber" or "pypdf"
    parse_success: bool               # False if fewer than MIN_FIELDS extracted
    raw_fields: dict[str, str]        # country-specific label → extracted text value
    missing_fields: list[str]         # normalized field keys that could not be extracted
    extraction_notes: list[str]       # warnings (e.g., "AUM text truncated", "holding list partial")
```

### 3.2 `raw_fields` key conventions per country

The `raw_fields` dict stores country-native labels as keys. The normalizer maps these to canonical keys.

**India (Groww):**
```python
raw_fields = {
    "NAV": "₹98.45",
    "AUM": "₹5,234 Cr",
    "Expense Ratio": "0.67%",
    "Exit Load": "1% for redemption within 1 year",
    "Min SIP Amount": "₹500",
    "Min Lumpsum": "₹5,000",
    "Risk": "Very High",                         # riskometer label
    "Benchmark": "Nifty Healthcare TRI",
    "Fund Manager": "Chirag Setalvad",
    "Fund House": "HDFC Mutual Fund",
    "Investment Objective": "...",
    "Top 10 Holdings": "Sun Pharma | 9.2%, ...",
    "Sector": "Pharma | Healthcare",
}
```

**USA (ETF.com / issuer):**
```python
raw_fields = {
    "Net Assets": "$42.1B",
    "Expense Ratio": "0.09%",
    "NAV": "$148.72",
    "Market Price": "$148.68",
    "Benchmark Index": "Health Care Select Sector Index",
    "Issuer": "State Street Global Advisors",
    "Investment Objective": "...",
    "Top Holdings": "UnitedHealth Group | 12.4%, ...",
    "# Holdings": "65",
}
```

**Canada (TMX / issuer):**
```python
raw_fields = {
    "MER": "0.85%",
    "Management Fee": "0.65%",
    "NAV": "CA$10.24",
    "Net Assets": "CA$621M",
    "Risk Rating": "Medium",
    "Benchmark": "Solactive Healthcare Leaders Index",
    "Manager": "Harvest Portfolios Group",
    "Investment Objective": "...",
}
```

**UK/Europe (JustETF / issuer):**
```python
raw_fields = {
    "TER": "0.35%",
    "Fund Size": "USD 1.2B",
    "NAV": "USD 97.45",
    "SRRI": "6",
    "Replication": "Physical (Optimized sampling)",
    "Distribution Policy": "Accumulating",
    "Issuer": "BlackRock Asset Management Ireland Limited",
    "Investment Objective": "...",
    "ISIN": "IE00B43HR379",
}
```

### 3.3 Validation Rules

| Rule | Detail |
|---|---|
| `parse_success = True` | At least 3 of these keys must be non-empty: `fund_name`, any cost_ratio field, any risk field, `benchmark`, `investment_objective` |
| `raw_fields` values | Strip leading/trailing whitespace; truncate at 2000 chars per value |
| `missing_fields` | Computed as: normalized_field_keys that have no extractable counterpart in `raw_fields` |

---

## 4. NormalizedFund — `ingestion/normalizer.py` output

All country-specific terminology is mapped to canonical normalized field names. This is the last structured model before chunking.

### 4.1 Python Dataclass

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class NormalizedFund:
    # Identity (always populated; sourced from FundSource + ParsedFund)
    fund_id: str
    country_or_market: str              # India | USA | Canada | China/HK | Japan | Singapore | UK/Europe
    fund_name: str
    ticker_or_identifier: str | None    # ticker for ETFs; ISIN for UCITS; null for India MFs
    fund_type: str                      # Mutual Fund | ETF | UCITS ETF | Fund | Index
    domain_subcategory: str             # Pharma | Broad Healthcare | Biotech | Med-Tech | Healthcare Innovation
    currency: str                       # ISO 4217 code
    exchange: str | None

    # Source provenance
    source_type: str                    # "official" or "platform" or "pdf"
    platform_url: str
    official_url: str | None
    last_updated_from_source: str | None   # date string extracted from page (e.g., "May 2026")
    fetch_timestamp: str                   # ISO 8601

    # Normalized financial fields (all optional — not every market publishes all fields)
    nav_or_price: str | None               # current NAV or market price with currency symbol
    aum: str | None                        # AUM / Net Assets / Fund Size with currency + unit
    expense_ratio_or_mer_or_ter: str | None  # cost ratio as percentage string e.g. "0.09%"
    minimum_investment: str | None         # minimum lumpsum / investment amount
    minimum_sip: str | None                # India-specific; null for ETFs
    exit_load_or_redemption_fee: str | None
    benchmark: str | None                  # index name
    fund_management: str | None            # manager name(s)
    fund_house_or_issuer: str | None       # AMC / issuer / asset manager name
    investment_objective: str | None       # official objective statement (can be long)
    risk_rating_or_riskometer: str | None  # text label or numeric scale value
    distribution_policy: str | None        # Accumulating | Distributing | Dividend
    tax_information: str | None            # any tax notes from source

    # Holdings and exposures (list / dict types)
    top_10_holdings: list[dict] | None     # see Holding sub-model (Section 4.2)
    sector_exposure: list[dict] | None     # see Exposure sub-model (Section 4.3)
    geographic_exposure: list[dict] | None # see Exposure sub-model (Section 4.3)

    # Document links
    documents: list[str] | None           # factsheet, prospectus, Fund Facts PDF URLs

    # Audit / debugging
    raw_fields: dict[str, str]            # preserved for audit; not used in chunking or retrieval
    missing_fields: list[str]             # normalized field keys with no value
    extraction_notes: list[str]           # warnings from parse stage
```

### 4.2 Holding Sub-model

Used inside `top_10_holdings`.

```python
@dataclass
class Holding:
    name: str            # company / security name
    weight: str | None   # percentage as string: "12.4%"
    ticker: str | None   # holding's ticker if available
    isin: str | None     # holding's ISIN if available
```

JSON example:
```json
{
  "name": "UnitedHealth Group Inc",
  "weight": "12.4%",
  "ticker": "UNH",
  "isin": null
}
```

### 4.3 Exposure Sub-model

Used inside `sector_exposure` and `geographic_exposure`.

```python
@dataclass
class Exposure:
    label: str           # sector name or country/region name
    weight: str | None   # percentage as string: "45.2%"
```

JSON example (sector):
```json
{"label": "Pharmaceuticals", "weight": "45.2%"}
```

JSON example (geographic):
```json
{"label": "United States", "weight": "68.3%"}
```

### 4.4 Full JSON Example — `NormalizedFund` for XLV

```json
{
  "fund_id": "usa_xlv",
  "country_or_market": "USA",
  "fund_name": "Health Care Select Sector SPDR ETF",
  "ticker_or_identifier": "XLV",
  "fund_type": "ETF",
  "domain_subcategory": "Broad Healthcare",
  "currency": "USD",
  "exchange": "NYSE Arca",
  "source_type": "official",
  "platform_url": "https://www.etf.com/XLV",
  "official_url": "https://www.ssga.com/us/en/intermediary/etfs/state-street-health-care-select-sector-spdr-etf-xlv",
  "last_updated_from_source": "2026-06-01",
  "fetch_timestamp": "2026-06-02T10:03:41+05:30",
  "nav_or_price": "USD 148.72",
  "aum": "USD 42.1B",
  "expense_ratio_or_mer_or_ter": "0.09%",
  "minimum_investment": null,
  "minimum_sip": null,
  "exit_load_or_redemption_fee": null,
  "benchmark": "Health Care Select Sector Index",
  "fund_management": "State Street Global Advisors",
  "fund_house_or_issuer": "State Street Global Advisors (SSGA)",
  "investment_objective": "Seeks to provide investment results that, before expenses, correspond generally to the price and yield performance of the Health Care Select Sector Index.",
  "risk_rating_or_riskometer": null,
  "distribution_policy": "Distributing",
  "tax_information": null,
  "top_10_holdings": [
    {"name": "UnitedHealth Group Inc", "weight": "12.4%", "ticker": "UNH", "isin": null},
    {"name": "Eli Lilly and Co", "weight": "11.8%", "ticker": "LLY", "isin": null},
    {"name": "Johnson & Johnson", "weight": "8.3%", "ticker": "JNJ", "isin": null}
  ],
  "sector_exposure": [
    {"label": "Pharmaceuticals", "weight": "28.4%"},
    {"label": "Health Care Equipment & Supplies", "weight": "16.2%"},
    {"label": "Managed Health Care", "weight": "15.9%"}
  ],
  "geographic_exposure": [
    {"label": "United States", "weight": "100%"}
  ],
  "documents": null,
  "raw_fields": {"Net Assets": "$42.1B", "Expense Ratio": "0.09%"},
  "missing_fields": ["minimum_investment", "risk_rating_or_riskometer", "tax_information"],
  "extraction_notes": []
}
```

### 4.5 Full JSON Example — `NormalizedFund` for HDFC Pharma (India)

```json
{
  "fund_id": "india_hdfc_pharma",
  "country_or_market": "India",
  "fund_name": "HDFC Pharma and Healthcare Fund Direct Growth",
  "ticker_or_identifier": null,
  "fund_type": "Mutual Fund",
  "domain_subcategory": "Pharma / Broad Healthcare",
  "currency": "INR",
  "exchange": "BSE / NSE",
  "source_type": "platform",
  "platform_url": "https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth",
  "official_url": null,
  "last_updated_from_source": "2026-06-02",
  "fetch_timestamp": "2026-06-02T10:00:58+05:30",
  "nav_or_price": "INR 98.45",
  "aum": "INR 5,234 Cr",
  "expense_ratio_or_mer_or_ter": "0.67%",
  "minimum_investment": "INR 5,000",
  "minimum_sip": "INR 500",
  "exit_load_or_redemption_fee": "1% for redemption within 1 year",
  "benchmark": "Nifty Healthcare TRI",
  "fund_management": "Chirag Setalvad",
  "fund_house_or_issuer": "HDFC Mutual Fund",
  "investment_objective": "To generate long-term capital appreciation from a portfolio predominantly invested in equity and equity related securities of companies engaged in the healthcare, pharmaceutical and related sectors.",
  "risk_rating_or_riskometer": "Very High",
  "distribution_policy": null,
  "tax_information": null,
  "top_10_holdings": [
    {"name": "Sun Pharmaceuticals Industries Ltd", "weight": "9.2%", "ticker": null, "isin": null},
    {"name": "Cipla Ltd", "weight": "7.8%", "ticker": null, "isin": null}
  ],
  "sector_exposure": [
    {"label": "Pharmaceuticals", "weight": "72.3%"},
    {"label": "Healthcare Services", "weight": "18.5%"}
  ],
  "geographic_exposure": [
    {"label": "India", "weight": "100%"}
  ],
  "documents": null,
  "raw_fields": {"NAV": "₹98.45", "AUM": "₹5,234 Cr", "Expense Ratio": "0.67%"},
  "missing_fields": ["distribution_policy", "tax_information"],
  "extraction_notes": []
}
```

---

## 5. Chunk — `ingestion/chunker.py` output + ChromaDB unit

The unit of retrieval. One chunk per semantic section per fund. Stored in ChromaDB.

### 5.1 Python Dataclass

```python
@dataclass
class Chunk:
    # Storage key
    chunk_id: str                      # "<fund_id>_<section>" e.g. "usa_xlv_cost_ratio"

    # Content
    section: str                       # normalized section key (see Section 5.2)
    text: str                          # formatted text for embedding and LLM context

    # Retrieval metadata (indexed in ChromaDB — all must be str or int for ChromaDB compatibility)
    fund_id: str
    country: str
    fund_name: str
    ticker: str                        # empty string "" if null (ChromaDB does not store None)
    isin: str                          # empty string "" if null
    domain_subcategory: str
    fund_type: str
    source_type: str                   # "official" or "platform" or "pdf"
    source_url: str                    # the URL this chunk's content came from
    official_url: str                  # empty string "" if null
    platform_url: str
    last_updated_from_source: str      # empty string "" if unknown
    fetch_timestamp: str               # ISO 8601
```

### 5.2 Section Keys and Source Fields

| `section` key | Source field in NormalizedFund | Notes |
|---|---|---|
| `overview` | `fund_name` + `fund_type` + `domain_subcategory` + `investment_objective` (first 100 chars) | Short summary chunk; always created |
| `cost_ratio` | `expense_ratio_or_mer_or_ter` | Normalized term used in chunk text |
| `risk` | `risk_rating_or_riskometer` | |
| `benchmark` | `benchmark` | |
| `investment_objective` | `investment_objective` | Full text |
| `fund_management` | `fund_management` | |
| `fund_house_or_issuer` | `fund_house_or_issuer` | |
| `nav_or_price` | `nav_or_price` | |
| `aum` | `aum` | |
| `top_10_holdings` | `top_10_holdings` | Serialized to readable text |
| `sector_exposure` | `sector_exposure` | |
| `geographic_exposure` | `geographic_exposure` | |
| `minimum_investment` | `minimum_investment` + `minimum_sip` | Combined into one chunk |
| `exit_load` | `exit_load_or_redemption_fee` | |
| `distribution_policy` | `distribution_policy` | |
| `documents` | `documents` | |
| `identity` | `ticker_or_identifier` + `isin` + `exchange` + `currency` | Metadata chunk for ticker lookups |

### 5.3 Text Format Rules

Chunk text is prefixed with fund identity for embedding quality:

```
[{fund_name} | {country} | {section_label}]
{content}
```

Examples:

```
# cost_ratio chunk for XLV
[Health Care Select Sector SPDR ETF | USA | Expense Ratio]
The expense ratio (cost ratio) of XLV is 0.09%.

# top_10_holdings chunk for HDFC Pharma
[HDFC Pharma and Healthcare Fund Direct Growth | India | Top 10 Holdings]
Top 10 Holdings:
1. Sun Pharmaceuticals Industries Ltd — 9.2%
2. Cipla Ltd — 7.8%

# risk chunk for HHL Canada
[Harvest Healthcare Leaders Income ETF | Canada | Risk]
The risk rating (MER-equivalent: risk rating) of HHL is Medium.

# minimum_investment chunk for HDFC Pharma
[HDFC Pharma and Healthcare Fund Direct Growth | India | Minimum Investment]
Minimum SIP: INR 500. Minimum lumpsum investment: INR 5,000.
```

### 5.4 Qdrant Point Schema

```python
# How each Chunk maps to a Qdrant upsert call (embeddings/store.py):
client.upsert(
    collection_name="healthcare_funds",
    points=[PointStruct(
        id="<uuid5 of 'usa_xlv_cost_ratio'>",   # deterministic UUID string
        vector=[0.023, -0.147, ...],              # 768-dim multilingual-e5-base vector
        payload={
            "chunk_id":                  "usa_xlv_cost_ratio",
            "fund_id":                   "usa_xlv",
            "section":                   "cost_ratio",
            "country":                   "USA",
            "fund_name":                 "Health Care Select Sector SPDR ETF",
            "ticker":                    "XLV",
            "isin":                      "",
            "domain_subcategory":        "Broad Healthcare",
            "fund_type":                 "ETF",
            "source_type":               "official",
            "source_url":                "https://www.ssga.com/...",
            "official_url":              "https://www.ssga.com/...",
            "platform_url":              "https://www.etf.com/XLV",
            "last_updated_from_source":  "2026-06-01",
            "fetch_timestamp":           "2026-06-02T10:03:41+05:30",
            "text":                      "[Health Care Select Sector SPDR ETF | USA | Expense Ratio]\nThe expense ratio of XLV is 0.09%.",
        }
    )]
)
```

Payload indices (created automatically at collection init):
`fund_id`, `country`, `section`, `ticker`, `isin`, `source_type`, `domain_subcategory`

### 5.5 Chunk Validation Rules

| Rule | Detail |
|---|---|
| Minimum text length | 20 tokens (~80 chars); discard if below (likely empty field) |
| Maximum text length | 512 tokens (~2000 chars); split into sub-chunks if exceeded; each sub-chunk gets a suffix: `_part1`, `_part2` |
| `chunk_id` uniqueness | UUID5 derived from chunk_id ensures deterministic, collision-free point IDs |
| Empty section | If source field is None or empty string → do NOT create chunk; record in `missing_fields` |
| Metadata values | Qdrant payload accepts mixed types; `None` → `""` (empty string) |

### 5.6 Expected Chunk Counts

| Country | Funds | Avg sections/fund | Expected chunks |
|---|---|---|---|
| India | 5 | 12 (no distribution_policy) | ~60 |
| USA | 5 | 15 | ~75 |
| Canada | 5 | 14 | ~70 |
| China/HK | 5 | 10 (sparser data) | ~50 |
| Japan | 4 | 10 | ~40 |
| UK/Europe | 5 | 13 | ~65 |
| Singapore | 4–5 | 8 (fewer fields) | ~40 |
| **Total** | **~34** | | **~400 chunks** |

---

## 6. BotResponse — `llm/response_formatter.py` output

Internal response model produced by the LLM layer before serialization to the API model.

### 6.1 Python Dataclass

```python
@dataclass
class BotResponse:
    answer: str                    # LLM-generated answer text
    source_url: str                # official_url if available; else platform_url
    platform_url: str | None       # shown as secondary "Also see" link in UI
    last_updated: str | None       # last_updated_from_source from the best chunk
    fetch_timestamp: str | None    # fetch_timestamp from the best chunk
    is_refusal: bool               # True if guardrail triggered (no retrieval ran)
    intent: str                    # FACTUAL | COMPARISON | ADVICE | OUT_OF_SCOPE
    chunks_used: list[str]         # chunk_ids of retrieved chunks that informed the answer (for audit)
    missing_data: bool             # True if no chunks were found and missing-data response was returned
```

### 6.2 JSON Examples

**Factual answer:**
```json
{
  "answer": "The expense ratio of the Health Care Select Sector SPDR ETF (XLV) is 0.09%.",
  "source_url": "https://www.ssga.com/us/en/intermediary/etfs/state-street-health-care-select-sector-spdr-etf-xlv",
  "platform_url": "https://www.etf.com/XLV",
  "last_updated": "2026-06-01",
  "fetch_timestamp": "2026-06-02T10:03:41+05:30",
  "is_refusal": false,
  "intent": "FACTUAL",
  "chunks_used": ["usa_xlv_cost_ratio"],
  "missing_data": false
}
```

**Refusal:**
```json
{
  "answer": "I can't provide investment advice or buy/sell recommendations. I can help with factual details such as expense ratio, AUM, benchmark, holdings, risk rating, investment objective, and official source documents. What factual information would you like to know?",
  "source_url": null,
  "platform_url": null,
  "last_updated": null,
  "fetch_timestamp": null,
  "is_refusal": true,
  "intent": "ADVICE",
  "chunks_used": [],
  "missing_data": false
}
```

**Missing data:**
```json
{
  "answer": "I could not find this information in the current source set for this fund.",
  "source_url": null,
  "platform_url": null,
  "last_updated": null,
  "fetch_timestamp": null,
  "is_refusal": false,
  "intent": "FACTUAL",
  "chunks_used": [],
  "missing_data": true
}
```

---

## 7. ChatRequest / ChatResponse — `api/models.py` (Pydantic)

API boundary models. Validated by FastAPI on every `/chat` call.

### 7.1 `ChatRequest`

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="User's natural language question about healthcare funds",
        example="What is the expense ratio of HDFC Pharma and Healthcare Fund?"
    )
    country: str | None = Field(
        default=None,
        description="Optional country filter from UI dropdown. One of: India | USA | Canada | China/HK | Japan | Singapore | UK/Europe",
        example="USA"
    )
    fund_id: str | None = Field(
        default=None,
        description="Optional fund_id filter from UI dropdown. Must match a fund id in sources.yaml",
        example="usa_xlv"
    )
```

### 7.2 `ChatResponse`

```python
class ChatResponse(BaseModel):
    answer: str = Field(
        ...,
        description="Factual answer or refusal message"
    )
    source_url: str | None = Field(
        default=None,
        description="Primary source URL (official_url preferred over platform_url)"
    )
    platform_url: str | None = Field(
        default=None,
        description="Secondary platform URL for user reference"
    )
    last_updated: str | None = Field(
        default=None,
        description="Last updated date from the source document or page"
    )
    fetch_timestamp: str | None = Field(
        default=None,
        description="ISO 8601 timestamp of when the bot last fetched this source"
    )
    is_refusal: bool = Field(
        ...,
        description="True if the query was refused (advice, OOS, or ambiguous)"
    )
    intent: str = Field(
        ...,
        description="Classified intent: FACTUAL | COMPARISON | ADVICE | OUT_OF_SCOPE"
    )
    missing_data: bool = Field(
        default=False,
        description="True if query was valid but corpus had no matching data"
    )
    fund_name: str | None = Field(
        default=None,
        description="Name of the primary fund the answer concerns — used by the frontend to append fund context to follow-up suggestion chips"
    )
```

### 7.3 `FundListItem` (for `/funds` and `/funds/{country}` endpoints)

```python
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
```

---

## 8. IngestionLog — `logs/ingestion.log` structure

Each ingestion run writes one JSON log entry per fund + URL.

### 8.1 JSON Schema

```json
{
  "run_id": "2026-06-02T10:00:00+05:30",
  "fund_id": "india_hdfc_pharma",
  "fetch_url": "https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth",
  "source_type": "platform",
  "fetch_method": "playwright",
  "http_status": 200,
  "fetch_success": true,
  "parse_success": true,
  "fetch_timestamp": "2026-06-02T10:00:58+05:30",
  "fields_extracted": [
    "nav_or_price", "aum", "expense_ratio_or_mer_or_ter",
    "minimum_investment", "minimum_sip", "exit_load_or_redemption_fee",
    "benchmark", "fund_management", "fund_house_or_issuer",
    "investment_objective", "risk_rating_or_riskometer", "top_10_holdings",
    "sector_exposure"
  ],
  "fields_missing": ["distribution_policy", "tax_information", "geographic_exposure", "documents"],
  "chunks_upserted": 13,
  "chunks_skipped": 3,
  "error_message": null
}
```

### 8.2 Error Entry Example

```json
{
  "run_id": "2026-06-02T10:00:00+05:30",
  "fund_id": "hk_2820_yahoo",
  "fetch_url": "https://finance.yahoo.com/quote/2820.HK/",
  "source_type": "platform",
  "fetch_method": "requests",
  "http_status": 429,
  "fetch_success": false,
  "parse_success": false,
  "fetch_timestamp": "2026-06-02T10:05:12+05:30",
  "fields_extracted": [],
  "fields_missing": ["all"],
  "chunks_upserted": 0,
  "chunks_skipped": 0,
  "error_message": "HTTP 429 Too Many Requests. Previous chunks retained in ChromaDB."
}
```

---

## 9. Normalization Map — `config/normalization.yaml` (full)

Maps country-specific raw field labels to normalized field keys.

```yaml
# Structure: normalized_key → country → [list of raw label variants]
# Matching is case-insensitive; partial match is acceptable

cost_ratio:
  India:    ["expense ratio", "total expense ratio", "ter"]
  USA:      ["expense ratio", "gross expense ratio", "net expense ratio", "total annual fund operating expenses"]
  Canada:   ["mer", "management expense ratio", "management fee", "total mer"]
  China/HK: ["expense ratio", "management fee", "total expense ratio"]
  Japan:    ["expense ratio", "management fee", "total cost ratio"]
  UK/Europe: ["ter", "total expense ratio", "ongoing charges", "ongoing charge figure", "ocf"]
  Singapore: ["expense ratio", "ter", "management fee", "mer"]

risk:
  India:    ["riskometer", "risk level", "risk-o-meter"]
  USA:      ["risk level", "volatility"]
  Canada:   ["risk rating", "risk classification"]
  China/HK: ["risk level", "risk rating"]
  Japan:    ["risk level", "risk indicator"]
  UK/Europe: ["srri", "synthetic risk and reward indicator", "risk indicator", "risk rating"]
  Singapore: ["risk rating", "risk class", "risk level"]

fund_size:
  India:    ["aum", "assets under management", "fund size", "corpus"]
  USA:      ["net assets", "aum", "total net assets", "fund assets"]
  Canada:   ["net assets", "aum", "fund assets"]
  China/HK: ["net asset value", "fund size", "aum"]
  Japan:    ["net assets", "fund assets", "pure assets"]
  UK/Europe: ["fund size", "total net assets", "aum", "net assets"]
  Singapore: ["aum", "fund size", "net assets"]

price:
  India:    ["nav", "net asset value", "current nav"]
  USA:      ["nav", "market price", "closing price", "net asset value"]
  Canada:   ["nav", "market price", "net asset value"]
  China/HK: ["nav", "market price", "closing price"]
  Japan:    ["nav", "market price", "current price"]
  UK/Europe: ["nav", "net asset value", "market price"]
  Singapore: ["nav", "market price"]

exit_cost:
  India:    ["exit load", "redemption charge"]
  USA:      ["redemption fee", "sales load", "deferred sales charge", "cdsc"]
  Canada:   ["sales charge", "redemption fee", "dsc", "trailer fee"]
  China/HK: ["redemption fee", "exit fee"]
  Japan:    ["redemption fee", "exit fee"]
  UK/Europe: ["entry charge", "exit charge", "redemption charge"]
  Singapore: ["redemption fee", "exit fee", "sales charge"]

fund_manager:
  India:    ["fund manager", "managed by", "portfolio manager"]
  USA:      ["portfolio manager", "investment adviser", "advisor", "managed by"]
  Canada:   ["portfolio manager", "managed by", "investment manager"]
  China/HK: ["fund manager", "portfolio manager", "managed by"]
  Japan:    ["fund manager", "portfolio manager"]
  UK/Europe: ["investment manager", "portfolio manager", "fund manager", "managed by"]
  Singapore: ["fund manager", "portfolio manager", "investment manager"]

fund_house:
  India:    ["fund house", "amc", "asset management company", "mutual fund"]
  USA:      ["issuer", "adviser", "investment adviser", "fund company", "provider"]
  Canada:   ["manager", "management company", "issuer", "provider"]
  China/HK: ["issuer", "fund manager", "management company"]
  Japan:    ["management company", "issuer", "fund manager"]
  UK/Europe: ["issuer", "asset manager", "investment manager", "management company"]
  Singapore: ["fund manager", "issuer", "management company", "asset manager"]

min_investment:
  India:    ["minimum lumpsum", "min lumpsum", "minimum investment amount", "minimum purchase"]
  USA:      ["minimum investment", "investment minimum", "min investment"]
  Canada:   ["minimum investment", "min purchase", "minimum initial investment"]
  China/HK: ["minimum investment", "min subscription"]
  Japan:    ["minimum investment", "minimum subscription amount"]
  UK/Europe: ["minimum investment", "minimum subscription", "min initial investment"]
  Singapore: ["minimum investment", "minimum subscription"]

benchmark:
  India:    ["benchmark", "benchmark index", "performance benchmark"]
  USA:      ["benchmark index", "index tracked", "underlying index", "benchmark"]
  Canada:   ["benchmark", "underlying index", "reference index"]
  China/HK: ["benchmark", "underlying index", "reference index"]
  Japan:    ["benchmark", "target index"]
  UK/Europe: ["benchmark", "reference index", "underlying index", "tracked index"]
  Singapore: ["benchmark", "reference index"]
```

---

## 10. Controlled Vocabulary

### 10.1 `country_or_market` allowed values

```
India
USA
Canada
China/HK
Japan
Singapore
UK/Europe
```

### 10.2 `fund_type` allowed values

```
Mutual Fund
ETF
UCITS ETF
Fund
Index
```

### 10.3 `domain_subcategory` allowed values

```
Pharma
Broad Healthcare
Biotech
Med-Tech
Healthcare Innovation
Pharma / Broad Healthcare
Biotech / Med-Tech
```

### 10.4 `source_type` allowed values

```
platform
official
pdf
```

### 10.5 `intent` allowed values

```
FACTUAL
COMPARISON
ADVICE
OUT_OF_SCOPE
```

### 10.6 `section` allowed values

```
overview
cost_ratio
risk
benchmark
investment_objective
fund_management
fund_house_or_issuer
nav_or_price
aum
top_10_holdings
sector_exposure
geographic_exposure
minimum_investment
exit_load
distribution_policy
documents
identity
```

---

## 11. Field Presence Matrix

Which fields can realistically be populated per country, based on public source availability.

| Normalized Field | India | USA | Canada | China/HK | Japan | UK/Europe | Singapore |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| nav_or_price | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ~ |
| aum | ✓ | ✓ | ✓ | ~ | ~ | ✓ | ~ |
| expense_ratio_or_mer_or_ter | ✓ | ✓ | ✓ | ~ | ~ | ✓ | ~ |
| minimum_investment | ✓ | ~ | ~ | ~ | ~ | ~ | ~ |
| minimum_sip | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| exit_load_or_redemption_fee | ✓ | ~ | ~ | ~ | ~ | ~ | ~ |
| benchmark | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ~ |
| fund_management | ✓ | ✓ | ✓ | ~ | ~ | ~ | ~ |
| fund_house_or_issuer | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| investment_objective | ✓ | ✓ | ✓ | ~ | ~ | ✓ | ✓ |
| risk_rating_or_riskometer | ✓ | ~ | ✓ | ~ | ~ | ✓ | ~ |
| top_10_holdings | ✓ | ✓ | ~ | ~ | ~ | ✓ | ~ |
| sector_exposure | ✓ | ✓ | ~ | ~ | ~ | ✓ | ~ |
| geographic_exposure | ~ | ✓ | ~ | ~ | ~ | ✓ | ~ |
| distribution_policy | ✗ | ~ | ~ | ~ | ~ | ✓ | ~ |
| documents | ~ | ✓ | ✓ | ~ | ~ | ✓ | ✓ |

**Legend:** ✓ = consistently available · ~ = sometimes available · ✗ = not applicable

---

## 12. Model Relationships

```
FundSource (sources.yaml)
    │  1:1
    ▼
RawFetch (per URL fetched)
    │  1:1
    ▼
ParsedFund (per URL parsed)
    │  1:1
    ▼
NormalizedFund (per fund, merged from all URL parses)
    │  1:many
    ▼
Chunk (one per section, stored in ChromaDB)
    │  many:1
    ▼  (retrieved at query time)
BotResponse (one per user query)
    │  1:1
    ▼
ChatResponse (Pydantic, returned to Streamlit)
```

**Merge note:** A single fund has both a platform URL and an official URL. Two `ParsedFund` objects are produced per fund. The `normalizer.py` merges them into one `NormalizedFund`, preferring official-source values when both populate the same field.

---

## 13. ChromaDB Query Filter Reference

Valid metadata field names for ChromaDB `where` clauses:

```python
# Single-value exact match
{"country": "USA"}
{"fund_id": "usa_xlv"}
{"ticker": "XLV"}
{"section": "cost_ratio"}
{"source_type": "official"}
{"domain_subcategory": "Biotech"}

# Compound AND filter (ChromaDB $and operator)
{"$and": [{"country": "Canada"}, {"section": "cost_ratio"}]}
{"$and": [{"country": "USA"}, {"ticker": "XLV"}]}

# Multi-value OR for country-wise queries
{"country": {"$in": ["India", "USA", "Canada"]}}

# Retrieve overview chunks for all funds in corpus
{"section": "overview"}
```

---

## 14. Data Size Estimates

| Item | Estimate |
|---|---|
| Total FundSource entries | 34 primary + 4 backup = 38 |
| Total URLs fetched per run | ~65 (platform + official + some PDFs) |
| Total RawFetch files stored | ~65 HTML/PDF files per daily run |
| Total NormalizedFund objects | 34 per run |
| Total Chunks in ChromaDB | ~400 (steady state) |
| Average chunk text size | 80–400 chars |
| ChromaDB vector dimensions | 384 (BGE-small) |
| Estimated vector store size | ~400 vectors × 384 floats × 4 bytes ≈ 600 KB |
| Ingestion log size per run | ~38 JSON entries ≈ 15 KB |
