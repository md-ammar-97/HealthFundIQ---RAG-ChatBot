# Problem Statement: Global Healthcare Funds RAG Assistant

## 1. Project Title

**Global Healthcare Funds RAG Assistant**

A facts-only Retrieval-Augmented Generation (RAG) chatbot that helps users ask factual questions about healthcare, pharma, biotech, med-tech, and healthcare innovation funds across multiple countries using public, no-login fund information pages and official source documents.

---

## 2. Background and Context

Retail investors often explore funds through simple public platforms such as Groww in India, where users can view basic fund information without logging in. These pages usually contain useful facts such as NAV, AUM, expense ratio, minimum SIP/lumpsum amount, exit load, risk level, benchmark, objective, fund management details, and fund house information.

However, when users want to compare similar funds across countries, there is no single Groww-like platform that covers India, USA, Canada, China, Singapore, Hong Kong, Japan, and the UK in a consistent way. Each market has its own public platforms, issuer websites, exchange pages, factsheets, and regulatory documents.

This project aims to build a small but well-scoped RAG chatbot around one investment domain: **Healthcare / Pharma / Biotech**. The bot will collect public fund information from India and other global markets, normalize it into comparable sections, and answer factual questions with source links.

The system will not provide investment advice, buy/sell recommendations, portfolio allocation guidance, expected returns, or personalized recommendations. It will only answer fact-based questions from the collected corpus.

---

## 3. Domain Selection

### Selected Domain

**Healthcare / Pharma / Biotech / Med-Tech / Healthcare Innovation**

### Reason for Selecting This Domain

Healthcare is a strong domain for this project because:

1. India has multiple healthcare/pharma mutual funds available on Groww and official AMC websites.
2. The USA has large and well-documented healthcare ETFs.
3. Canada has public ETF pages and issuer factsheets for healthcare funds.
4. China and Hong Kong have biotech and healthcare ETFs.
5. Japan has pharmaceutical and bio/med-tech ETFs.
6. The UK and Europe have multiple UCITS healthcare ETFs.
7. Healthcare funds usually publish comparable factual fields such as AUM, NAV, expense ratio/MER, holdings, benchmark, risk level, objective, and fund manager.

AI-focused funds were considered, but healthcare was selected because AI-specific funds are not consistently available across all target countries, whereas healthcare/pharma/biotech funds are easier to identify globally.

---

## 4. Problem to Solve

Users who want to compare healthcare-related investment funds across countries currently face several problems:

1. **Information is scattered across different platforms**
   - India uses Groww-style mutual fund pages.
   - USA uses ETF.com, issuer pages, SEC filings, and fund provider pages.
   - Canada uses TMX Money, issuer pages, and Fund Facts documents.
   - Hong Kong and China use HKEX, Yahoo Finance, and issuer websites.
   - Japan uses issuer pages and market quote platforms.
   - UK/Europe uses JustETF and issuer pages.

2. **Terminology differs by country**
   - India uses terms like expense ratio, exit load, SIP, riskometer, and direct growth.
   - Canada uses MER, Fund Facts, management fee, and risk rating.
   - USA uses expense ratio, NAV, market price, prospectus, and holdings.
   - UK/Europe uses TER, UCITS, fund size, distribution policy, and replication method.

3. **Users struggle to compare similar funds country-wise**
   - There is no single lightweight tool that lets users ask:  
     “Which healthcare funds are available in India vs USA vs Canada?”  
     “What is the expense ratio/MER of each fund?”  
     “Which fund is pharma-focused vs broad healthcare?”  
     “Which country has the largest healthcare fund in this corpus?”

4. **General LLMs may hallucinate financial facts**
   - Fund facts change frequently.
   - LLMs may provide outdated or unsupported information.
   - Every factual answer must be grounded in retrieved source content.

5. **Financial safety is critical**
   - Users may ask for advice, buy/sell recommendations, return predictions, or portfolio allocation suggestions.
   - The assistant must refuse such queries and respond only with facts and educational context.

---

## 5. Project Objective

The objective is to build a **facts-only global healthcare funds RAG chatbot** that can:

1. Ingest public fund pages and official fund documents.
2. Extract and normalize fund-level facts.
3. Answer factual questions about healthcare/pharma/biotech funds.
4. Compare funds country-wise using only retrieved source data.
5. Provide at least one clear source link with every answer.
6. Refuse investment advice, portfolio recommendations, and performance predictions.
7. Maintain transparency by showing the source and last-updated information.

---

## 6. Target Users

### Primary Users

1. Retail investors exploring healthcare/pharma/biotech funds.
2. Product teams building financial information assistants.
3. Support/content teams answering repetitive fund-related questions.
4. Students or analysts learning how sector funds differ across countries.

### Secondary Users

1. Developers learning RAG implementation.
2. Product managers designing financial AI assistants.
3. Researchers comparing public financial disclosure formats across countries.

---

## 7. Core Use Cases

The chatbot should answer factual questions such as:

1. “What is the expense ratio of HDFC Pharma and Healthcare Fund?”
2. “What is the MER of a Canadian healthcare ETF?”
3. “Which USA healthcare ETF has the largest AUM in the corpus?”
4. “What benchmark does XLV track?”
5. “Who manages Nippon India Pharma Fund?”
6. “Which funds in the corpus focus on biotech?”
7. “Which healthcare funds are available for India, USA, and Canada?”
8. “What is the investment objective of VHT?”
9. “What is the risk level/risk rating of this fund?”
10. “Show the top holdings of a selected healthcare ETF.”
11. “Which fund is pharma-focused and which is broad healthcare?”
12. “What is the fund house or issuer for each country?”

---

## 8. Out-of-Scope Use Cases

The chatbot must not answer or must politely refuse:

1. “Should I invest in this fund?”
2. “Which fund should I buy?”
3. “Is this fund better than that fund?”
4. “Will this fund give high returns?”
5. “Build a portfolio for me.”
6. “How much should I invest?”
7. “Which fund will perform best next year?”
8. “Is this a good time to buy?”
9. “Predict the return of this ETF.”
10. “Tell me the best fund for my risk profile.”

The refusal should be polite, concise, and facts-only. It may redirect the user to official documents or educational resources.

Example refusal:

> I can only provide factual information from public sources and cannot give investment advice or buy/sell recommendations. You can ask about expense ratio, AUM, benchmark, holdings, objective, or risk rating of a fund.

---

## 9. Countries and Markets Covered

The first version will focus on the following markets:

1. India
2. USA
3. Canada
4. China
5. Hong Kong
6. Singapore
7. Japan
8. UK / Europe-listed UCITS funds

Some countries may have fewer than five directly comparable healthcare funds. In those cases, the system should include the best available public and official healthcare, pharma, biotech, or med-tech funds and clearly label the scope.

---

## 10. Corpus Strategy

The corpus will use two types of URLs:

### 10.1 Platform URLs

These are public no-login pages that behave like Groww-style discovery or quote pages.

Examples:

- Groww for India
- ETF.com for USA
- TMX Money for Canada
- Yahoo Finance for some international tickers
- HKEX for Hong Kong-listed ETFs
- JustETF for UK/Europe-listed UCITS ETFs
- SGX/FSMOne-style pages for Singapore where available

Platform URLs are useful for user-friendly display, quick comparison, and UI inspiration.

### 10.2 Official URLs

These are issuer, AMC, exchange, regulator, factsheet, prospectus, or official product pages.

Examples:

- HDFC Mutual Fund, Nippon India Mutual Fund, SBI Mutual Fund, ICICI Prudential AMC
- Vanguard, iShares, State Street, Fidelity, VanEck
- BlackRock Canada, Harvest ETFs, BMO ETFs, TD Asset Management, Global X Canada
- KraneShares, Global X Hong Kong, CSOP, ChinaAMC
- NEXT FUNDS Japan, Global X Japan
- iShares UK, State Street SPDR Europe, DWS Xtrackers, Invesco
- SEC, SEDAR+, exchange pages, factsheets, ETF Facts/Fund Facts documents

Official URLs should be preferred for citations in final answers.

---

## 11. Initial Fund Universe

### 11.1 India — Groww Platform URLs

India will use Groww-style public mutual fund pages for healthcare/pharma funds.

| No. | Fund | Platform URL |
|---:|---|---|
| 1 | HDFC Pharma and Healthcare Fund Direct Growth | `https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth` |
| 2 | Nippon India Pharma Fund Direct Growth | `https://groww.in/mutual-funds/nippon-india-pharma-fund-direct-growth` |
| 3 | Mirae Asset Healthcare Fund Direct Growth | `https://groww.in/mutual-funds/mirae-asset-healthcare-fund-direct-growth` |
| 4 | SBI Healthcare Opportunities Fund Direct Growth | `https://groww.in/mutual-funds/sbi-pharma-fund-direct-growth` |
| 5 | ICICI Prudential Pharma Healthcare and Diagnostics Fund Direct Growth | `https://groww.in/mutual-funds/icici-prudential-pharma-healthcare-and-diagnostics-%28p.h.d%29-fund-direct-growth` |

Optional India backup URLs:

| Fund | Platform URL |
|---|---|
| Tata India Pharma and Healthcare Fund Direct Growth | `https://groww.in/mutual-funds/tata-india-pharma-and-healthcare-fund-direct-growth` |
| UTI Healthcare Fund Direct Growth | `https://groww.in/mutual-funds/uti-pharma-and-healthcare-fund-direct-growth` |

---

### 11.2 USA — ETF.com and Official Issuer Pages

| No. | Fund | Ticker | Platform URL | Official URL |
|---:|---|---|---|---|
| 1 | Health Care Select Sector SPDR ETF | XLV | `https://www.etf.com/XLV` | `https://www.ssga.com/us/en/intermediary/etfs/state-street-health-care-select-sector-spdr-etf-xlv` |
| 2 | Vanguard Health Care ETF | VHT | `https://www.etf.com/VHT` | `https://investor.vanguard.com/investment-products/etfs/profile/vht` |
| 3 | iShares Global Healthcare ETF | IXJ | `https://www.etf.com/IXJ` | `https://www.ishares.com/us/products/239744/ishares-global-healthcare-etf` |
| 4 | iShares Biotechnology ETF | IBB | `https://www.etf.com/IBB` | `https://www.ishares.com/us/products/239699/ishares-biotechnology-etf` |
| 5 | Fidelity MSCI Health Care Index ETF | FHLC | `https://www.etf.com/FHLC` | `https://digital.fidelity.com/prgw/digital/research/quote/dashboard/summary?symbol=FHLC` |

Optional USA backup:

| Fund | Ticker | Platform URL | Official URL |
|---|---|---|---|
| VanEck Pharmaceutical ETF | PPH | `https://www.etf.com/PPH` | `https://www.vaneck.com/us/en/investments/pharmaceutical-etf-pph/` |

---

### 11.3 Canada — TMX Money and Official Issuer Pages

| No. | Fund | Ticker | Platform URL | Official URL |
|---:|---|---|---|---|
| 1 | Harvest Healthcare Leaders Income ETF | HHL | `https://money.tmx.com/en/quote/HHL` | `https://harvestportfolios.com/etf/hhl/` |
| 2 | iShares Global Healthcare Index ETF CAD-Hedged | XHC | `https://money.tmx.com/en/quote/XHC` | `https://www.blackrock.com/ca/investors/en/products/239743/ishares-global-healthcare-index-etf-cadhedged-fund` |
| 3 | BMO Equal Weight US Health Care Index ETF | ZHU | `https://money.tmx.com/en/quote/ZHU` | `https://bmogam.com/ca-en/products/exchange-traded-fund/bmo-equal-weight-us-health-care-index-etf-zhu/` |
| 4 | TD Global Healthcare Leaders Index ETF | TDOC | `https://money.tmx.com/en/quote/TDOC` | `https://www.td.com/ca/en/asset-management/funds/solutions/etfs/fundcard?fundId=7192&fundname=TD-Global-Healthcare-Leaders-Index-ETF` |
| 5 | Global X Equal Weight Global Healthcare Index ETF | MEDX | `https://money.tmx.com/en/quote/MEDX` | `https://www.globalx.ca/product/medx` |

Optional Canada backup:

| Fund | Ticker | Platform URL | Official URL |
|---|---|---|---|
| Evolve Global Healthcare Enhanced Yield Fund | LIFE | `https://finance.yahoo.com/quote/LIFE.TO/` | `https://evolveetfs.com/product/life/` |

---

### 11.4 China and Hong Kong — Yahoo Finance, HKEX, and Issuer Pages

China and Hong Kong overlap because many China-focused healthcare and biotech ETFs are listed in Hong Kong. The corpus should clearly label whether the fund is Hong Kong-listed, China-focused, or US-listed with China exposure.

| No. | Fund | Ticker | Platform URL | Official URL |
|---:|---|---|---|---|
| 1 | Global X China Biotech ETF | 2820.HK | `https://finance.yahoo.com/quote/2820.HK/` | `https://www.globalxetfs.com.hk/funds/china-biotech-etf/` |
| 2 | CSOP Hang Seng Biotech ETF | 3174.HK | `https://sg.finance.yahoo.com/quote/3174.HK/` | `https://www.csopasset.com/en/products/hk-health` |
| 3 | ChinaAMC Hang Seng Biotech ETF | 3069.HK | `https://finance.yahoo.com/quote/3069.HK/` | `https://www.chinaamc.com.hk/product/chinaamc-hang-seng-hong-kong-biotech-index-etf-3069-hk-9069-hk/` |
| 4 | KraneShares MSCI All China Health Care Index ETF | KURE | `https://finance.yahoo.com/quote/KURE/` | `https://kraneshares.com/etf/kure/` |
| 5 | Global X China Biotech ETF — HKEX Quote | 2820 | `https://www.hkex.com.hk/Market-Data/Securities-Prices/Exchange-Traded-Products/Exchange-Traded-Products-Quote?sc_lang=en&sym=2820` | `https://www.globalxetfs.com.hk/funds/china-biotech-etf/` |

---

### 11.5 Japan — Yahoo Finance and Issuer Pages

| No. | Fund | Ticker | Platform URL | Official URL |
|---:|---|---|---|---|
| 1 | NEXT FUNDS TOPIX-17 Pharmaceutical ETF | 1621.T | `https://finance.yahoo.com/quote/1621.T/` | `https://nextfunds.jp/en/lineup/1621/` |
| 2 | Global X Japan Bio & Med Tech ETF | 2639.T | `https://finance.yahoo.com/quote/2639.T/` | `https://globalxetfs.co.jp/en/funds/2639/index.html` |
| 3 | Global X HealthTech ETF | TBD | `https://globalxetfs.co.jp/en/funds/heal/` | `https://globalxetfs.co.jp/en/funds/heal/` |
| 4 | Global X Genomics & Biotechnology ETF | TBD | `https://globalxetfs.co.jp/en/funds/gnom/` | `https://globalxetfs.co.jp/en/funds/gnom/` |

Japan may have fewer than five directly comparable healthcare ETFs. The system should allow country-level corpus sizes to vary.

---

### 11.6 UK / Europe — JustETF and Official Issuer Pages

| No. | Fund | Identifier | Platform URL | Official URL |
|---:|---|---|---|---|
| 1 | iShares S&P 500 Health Care Sector UCITS ETF | IE00B43HR379 | `https://www.justetf.com/en/etf-profile.html?isin=IE00B43HR379` | `https://www.ishares.com/uk/individual/en/products/280507/ishares-sp-500-health-care-sector-ucits-etf` |
| 2 | iShares Healthcare Innovation UCITS ETF | IE00BYZK4776 | `https://www.justetf.com/en/etf-profile.html?isin=IE00BYZK4776` | `https://www.ishares.com/uk/individual/en/products/284216/ishares-healthcare-innovation-ucits-etf` |
| 3 | SPDR MSCI World Health Care UCITS ETF | IE00BYTRRB94 | `https://www.justetf.com/en/etf-profile.html?isin=IE00BYTRRB94` | `https://www.ssga.com/nl/en_gb/intermediary/etfs/state-street-spdr-msci-world-health-care-ucits-etf-whea-na` |
| 4 | Xtrackers MSCI World Health Care UCITS ETF | IE00BM67HK77 | `https://www.justetf.com/en/etf-profile.html?isin=IE00BM67HK77` | `https://etf.dws.com/en-ch/IE00BM67HK77-msci-world-health-care-ucits-etf-1c/` |
| 5 | Invesco US Health Care Sector UCITS ETF | IE00B3WMTH43 | `https://www.justetf.com/en/etf-profile.html?isin=IE00B3WMTH43` | Official Invesco product page to be added during source validation |

---

### 11.7 Singapore — Singapore-Accessible Healthcare Funds

Singapore may not have enough local healthcare ETFs. The system should treat this section as **Singapore-accessible healthcare funds**, not strictly Singapore-listed healthcare ETFs.

| No. | Fund / Source | Platform / Official URL |
|---:|---|---|
| 1 | Wellington Global Health Care Equity Fund | `https://www.wellington.com/en-sg/intermediary/funds/global-health-care-equity-fund` |
| 2 | Amova Asia Healthcare Fund | `https://sg.amova-am.com/general/funds/detail/amova-asia-healthcare-fund-jpy-class` |
| 3 | Amova Asia Healthcare Fund Factsheet PDF | `https://sg.amova-am.com/docs/default-source/sg-library/fund/factsheet/AMOVA-ASIA-HEALTHCARE-FUND-FACTSHEET.pdf` |
| 4 | Fidelity Funds Global Healthcare Fund Singapore | `https://www.fidelity.com.sg/investment/equity/global-healthcare` |
| 5 | SGX Healthcare Index | `https://www.sgx.com/indices/products/sgxhc` |

---

## 12. Data Fields to Extract

The system should extract and normalize the following sections where available:

```text
overview
country_or_market
fund_name
ticker_or_identifier
fund_type
domain_subcategory
nav_or_price
aum
expense_ratio_or_mer_or_ter
minimum_investment
minimum_sip
exit_load_or_redemption_fee
benchmark
fund_management
fund_house_or_issuer
investment_objective
risk_rating_or_riskometer
holdings
top_10_holdings
sector_exposure
geographic_exposure
distribution_policy
currency
exchange
tax_information
documents
platform_url
official_url
last_updated_from_source
fetch_timestamp
```

The system must gracefully handle missing fields because not every market publishes every field in the same format.

---

## 13. Data Normalization Requirements

Since each country uses different terminology, the system should normalize fields as follows:

| Normalized Field | India Term | USA Term | Canada Term | UK/Europe Term |
|---|---|---|---|---|
| Cost ratio | Expense ratio | Expense ratio | MER / management fee | TER / ongoing charge |
| Risk | Riskometer | Risk level | Risk rating | SRRI / risk indicator |
| Price | NAV | NAV / market price | NAV / market price | NAV / market price |
| Fund size | AUM | Net assets / AUM | Net assets / AUM | Fund size |
| Exit cost | Exit load | Redemption fee / sales load | Sales charge / redemption fee | Entry/exit charge |
| Investment minimum | Min SIP / lumpsum | Investment minimum | Minimum investment | Minimum investment |
| Fund manager | Fund manager | Portfolio manager / advisor | Portfolio manager | Investment manager |
| Fund house | AMC | Issuer / adviser | Manager / issuer | Issuer / asset manager |

---

## 14. RAG Answering Requirements

Every answer must follow these rules:

1. Answer only from retrieved corpus content.
2. Include at least one source link.
3. Keep the answer concise.
4. Do not provide investment advice.
5. Do not compute or predict future returns.
6. Do not rank funds as “best” unless the ranking is based on a factual field explicitly present in the corpus, such as AUM or expense ratio.
7. Mention if data is missing or unavailable.
8. Include “Last updated from sources” where available.
9. Prefer official URLs for citations.
10. Use platform URLs only for display or fallback when official data is not available.

---

## 15. Sample Acceptable Questions

The assistant should answer:

```text
What is the expense ratio of HDFC Pharma and Healthcare Fund?
What is the MER of HHL?
Which healthcare ETFs are available in Canada in this corpus?
Which fund tracks the Health Care Select Sector Index?
What is the benchmark of VHT?
Who is the issuer of IXJ?
What are the top holdings of IBB?
Which funds in the corpus are biotech-focused?
Which funds are India-focused healthcare funds?
Which funds are global healthcare funds?
Show healthcare funds available country-wise.
Which fund has the largest AUM among the collected US healthcare ETFs?
What is the investment objective of the Amova Asia Healthcare Fund?
```

---

## 16. Sample Refusal Questions

The assistant should refuse:

```text
Should I buy HDFC Pharma and Healthcare Fund?
Which healthcare fund is best for me?
Will XLV give better returns than VHT?
Can you build a healthcare portfolio for me?
Should I sell my existing pharma fund?
Which fund will go up next year?
How much money should I invest in IBB?
Is this the right time to buy healthcare ETFs?
```

---

## 17. Refusal Behavior

When refusing, the assistant should:

1. Be polite.
2. Explain that it can only provide facts.
3. Avoid giving a substitute recommendation.
4. Offer factual alternatives.

Example:

> I can’t provide investment advice or tell you whether to buy, sell, or hold a fund. I can help with factual information such as expense ratio, AUM, benchmark, holdings, risk rating, investment objective, and official source documents.

---

## 18. UI Requirements

The chatbot UI should be simple and transparent.

### Required UI Elements

1. Welcome message.
2. Domain note: “Healthcare / Pharma / Biotech funds.”
3. Country filter.
4. Fund filter.
5. Example questions.
6. Facts-only disclaimer.
7. Source link shown in every answer.
8. Last updated from source.
9. Clear refusal message for advice questions.

### Suggested Welcome Line

> Ask factual questions about healthcare, pharma, biotech, and med-tech funds across India, USA, Canada, China, Hong Kong, Singapore, Japan, and the UK. Facts only. No investment advice.

### Example Questions in UI

```text
What is the expense ratio of HDFC Pharma and Healthcare Fund?
Which healthcare funds are available in Canada?
What benchmark does XLV track?
Which funds in this corpus are biotech-focused?
Show healthcare funds country-wise.
```

### Disclaimer Snippet

> This assistant provides factual information from public sources only. It does not provide investment advice, buy/sell recommendations, portfolio allocation, return predictions, or personalized financial guidance. Always verify details from official fund documents before making financial decisions.

---

## 19. Key Constraints

### 19.1 Public Sources Only

The system must use publicly accessible URLs only. It must not require login, OTP, PAN, Aadhaar, account numbers, email, phone number, or private portfolio data.

### 19.2 No PII

The system must not accept, request, store, or process:

```text
PAN
Aadhaar
Account numbers
OTP
Email
Phone number
Broker login credentials
Demat details
Bank details
Portfolio screenshots
```

### 19.3 No Investment Advice

The system must not provide:

```text
Buy/sell recommendations
Portfolio construction
Personalized allocation
Return prediction
Timing advice
Risk-profile-based advice
Tax planning advice
```

### 19.4 No Unsupported Claims

The assistant must not answer from memory. If the answer is not available in the corpus, it should say:

> I could not find this information in the current source set.

### 19.5 Source Transparency

Every factual answer must include at least one source link.

---

## 20. Success Criteria

The project will be considered successful if:

1. The bot can ingest the selected fund URLs.
2. The bot can extract and chunk relevant fund facts.
3. The bot can answer factual fund questions with citations.
4. The bot refuses investment advice questions.
5. The bot supports country-wise comparison.
6. The bot handles missing fields gracefully.
7. The bot includes a simple UI with example questions and disclaimer.
8. The bot maintains source transparency.
9. The bot supports daily scheduled refresh.
10. The bot can be extended to additional countries, sectors, or fund types.

---

## 21. Known Limitations

1. Some international fund pages may use JavaScript-heavy rendering.
2. Some official pages may block automated scraping.
3. Some platforms may change page structure frequently.
4. Not every country has five clean healthcare-specific funds.
5. Some fields are not directly comparable across countries.
6. Currency conversion is out of scope unless added later.
7. Return comparison and performance ranking are out of scope.
8. The bot does not verify suitability for any user.
9. The bot does not provide investment advice.
10. Fund data may become stale unless scheduled refresh is working.

---

## 22. Proposed System Behavior

### If the user asks a factual question

The system should:

1. Identify the fund, country, and fact requested.
2. Retrieve the most relevant chunks.
3. Prefer official source chunks.
4. Generate a concise answer.
5. Include the source link.
6. Include last-updated information if available.

### If the user asks for comparison

The system should:

1. Identify the comparison field.
2. Retrieve structured facts for the selected funds.
3. Compare only factual fields available in the corpus.
4. Avoid advice-style language.
5. Clearly state missing values.

### If the user asks for investment advice

The system should:

1. Refuse politely.
2. State the facts-only limitation.
3. Offer factual alternatives.

### If data is unavailable

The system should say:

> I could not find this information in the current source set for this fund.

---

## 23. Example Output Format

### Factual Answer

```text
The HDFC Pharma and Healthcare Fund is a healthcare/pharma-focused equity mutual fund. The available source page includes fund details such as NAV, expense ratio, risk level, fund manager, AUM, and objective.

Source: https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth
Last updated from sources: <source_date_or_fetch_timestamp>
```

### Country-Wise Answer

```text
The current corpus includes healthcare-related funds from India, USA, Canada, China/Hong Kong, Japan, Singapore, and UK/Europe. India includes pharma/healthcare mutual funds, while the USA and Canada mostly include healthcare ETFs.

Source: <relevant_source_url>
Last updated from sources: <source_date_or_fetch_timestamp>
```

### Refusal Answer

```text
I can’t recommend whether you should buy or sell a fund. I can help with factual details such as expense ratio, AUM, benchmark, holdings, risk rating, and investment objective from public sources.
```

---

## 24. Suggested Technical Scope

### Phase 0 — Project Setup

Create the project structure, environment files, source list, and documentation.

### Phase 1 — Ingestion and Parsing

Fetch each corpus URL, save raw HTML/PDF/text, extract fund-specific content, and store cleaned text.

### Phase 2 — Chunking and Embeddings

Chunk content by semantic sections such as overview, expense ratio, benchmark, holdings, objective, risk, and documents. Use an open-source embedding model such as BGE small/base/large depending on chunk size and resource constraints.

### Phase 3 — Retrieval

Use metadata-aware retrieval with filters for country, fund, ticker, domain subcategory, and source type.

### Phase 4 — LLM Response Generation

Use Groq or another configured LLM to generate concise, citation-backed, facts-only answers.

### Phase 5 — Guardrails

Add refusal logic for advice, portfolio, prediction, and personalized financial questions.

### Phase 6 — UI

Build a simple Groww-inspired UI with country and fund filters, example questions, source display, and disclaimer.

### Phase 7 — Scheduler

Add a daily refresh scheduler to run at **10:00 AM IST**.

---

## 25. Final Product Statement

This project will build a **facts-only Global Healthcare Funds RAG Assistant** that helps users explore and compare healthcare, pharma, biotech, and med-tech funds across India, USA, Canada, China, Hong Kong, Singapore, Japan, and the UK.

The assistant will use public no-login platform pages and official fund documents to answer factual questions with citations. It will support country-wise comparison, normalize global fund terminology, handle missing data transparently, and refuse investment advice or personalized recommendations.

The first version will focus on a curated healthcare fund corpus. Future versions can extend the same architecture to other domains such as AI, clean energy, defense, semiconductors, fintech, or infrastructure.
