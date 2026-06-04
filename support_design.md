# support_design.md

# FinanceBot Support Design Specification

## 1. Design Recommendation

The best design for this Finance RAG chatbot is not a plain chat interface. It should be designed as a **Finance Research Workspace** for factual fund exploration.

The recommended product direction is:

> **AI Finance Research Terminal**  
> Ask a factual finance question → retrieve cited evidence → compare available facts → inspect source data → verify original links.

This design fits the project because FinanceBot is a facts-only RAG assistant for healthcare, pharma, biotech, med-tech, and healthcare innovation funds across India, USA, Canada, China/Hong Kong, Singapore, Japan, and UK/Europe. The UI must therefore make source transparency, factual comparison, and refusal boundaries visible at all times.

The design should combine:

| Layer | Recommended Inspiration | Purpose |
|---|---|---|
| Enterprise dashboard structure | IBM Carbon Design System | Clean data-heavy layouts, filters, tables, consistent spacing |
| RAG answer UX | Perplexity-style answer cards | Citations, source transparency, follow-up questions |
| Finance product UI | Groww / ET Money / Morningstar | Familiar fund cards, NAV/AUM/risk/expense displays |
| Frontend components | shadcn/ui + Tailwind CSS | Modern, flexible, fast to implement |
| Tables | TanStack Table | Sortable and filterable comparison grids |
| Charts | Recharts / Apache ECharts | Simple factual visualizations, only where data exists |
| Motion | Motion.dev / Framer Motion | Subtle state transitions, source panel reveal, card expansion |

**Final design principle:**

> Build FinanceBot as a **cited financial research assistant**, not as a conversational advice bot.

---

## 2. Product Context Used for Design

FinanceBot solves three main problems:

1. **Fragmented fund information** across Groww, ETF.com, TMX Money, Yahoo Finance, HKEX, JustETF, and official issuer/factsheet pages.
2. **Terminology mismatch** across markets, such as Expense Ratio vs MER vs TER.
3. **LLM hallucination risk**, because fund-level facts such as NAV, AUM, holdings, and expense ratios change frequently.

The UI must therefore support:

- Country-wise exploration.
- Fund-wise filtering.
- Factual question answering.
- Side-by-side comparison.
- Source verification.
- Missing-data transparency.
- No-advice guardrails.

The design should never imply that the bot is recommending investments, predicting returns, or giving personalized financial guidance.

---

## 3. Core UX Positioning

### 3.1 Product Name in UI

Recommended product display name:

> **FinanceBot Research Assistant**

Alternative names:

- Global Healthcare Funds Research AI
- Healthcare Funds Intelligence Workspace
- Finance RAG Research Terminal

Avoid names like:

- Best Fund AI
- Investment Advisor Bot
- Portfolio Recommender
- WealthGPT

These names create advice expectations and are not aligned with the project scope.

---

## 4. Information Architecture

The product should have four main user-facing areas.

```text
FinanceBot
├── Ask AI / Research Chat
├── Fund Explorer
├── Compare Funds
├── Sources & Evidence
└── About / Methodology
```

For MVP, these can be implemented as tabs or sidebar sections inside Streamlit. For a more polished portfolio version, they can become separate pages in a React/Next.js app.

---

## 5. Recommended Main Layout

### 5.1 Desktop Layout

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Top Bar: FinanceBot | Facts-only disclaimer | Last corpus refresh            │
├───────────────┬───────────────────────────────────────────────┬─────────────┤
│ Left Sidebar  │ Main Research Workspace                       │ Source Panel │
│               │                                               │             │
│ Country       │ Query input                                   │ Used sources │
│ Fund          │ Answer card                                   │ Official URL │
│ Type          │ Fact cards                                    │ Platform URL │
│ Subcategory   │ Comparison table                              │ Timestamp    │
│ Example Qs    │ Missing data notes                            │ Extracted    │
│               │ Suggested factual follow-ups                  │ snippets     │
└───────────────┴───────────────────────────────────────────────┴─────────────┘
```

### 5.2 Mobile Layout

On mobile, use a stacked layout:

```text
Top bar
Search / question box
Filters accordion
Answer card
Comparison cards
Sources accordion
Disclaimer footer
```

The source panel should become a collapsible section titled **Sources used**.

---

## 6. Screen-Level Design

## 6.1 Home / Welcome Screen

### Purpose

Introduce the assistant, clarify scope, and guide the user toward factual questions.

### Main Hero Copy

```text
Ask factual questions about global healthcare funds.
Compare public fund facts across India, USA, Canada, China/Hong Kong, Singapore, Japan, and UK/Europe.
```

### Subcopy

```text
FinanceBot answers only from retrieved public sources and official fund documents. It does not provide investment advice, buy/sell recommendations, return predictions, portfolio allocation, or personalized guidance.
```

### Primary Input Placeholder

```text
Ask about expense ratio, AUM, benchmark, holdings, risk rating, issuer, or investment objective...
```

### Example Prompt Chips

| Chip | Query |
|---|---|
| Expense ratio | What is the expense ratio of HDFC Pharma and Healthcare Fund? |
| Canada funds | Which healthcare ETFs are available in Canada? |
| Benchmark | What benchmark does XLV track? |
| Biotech focus | Which funds in this corpus are biotech-focused? |
| Country-wise | Show healthcare funds country-wise. |

### Required Disclaimer Banner

Use a persistent banner near the search area:

```text
Facts only. No investment advice. Always verify details from official fund documents before making financial decisions.
```

---

## 6.2 Ask AI / Research Chat Screen

### Purpose

Allow natural-language factual questions and show citation-backed answers.

### Components

1. **Question input**
2. **Country filter**
3. **Fund filter**
4. **Answer card**
5. **Fact summary chips**
6. **Source cards**
7. **Follow-up factual questions**
8. **Missing-data warning**
9. **Refusal message state**

### Answer Card Structure

```text
┌────────────────────────────────────────────────────┐
│ Answer                                             │
│                                                    │
│ [Concise factual response generated from chunks]   │
│                                                    │
│ Key facts                                          │
│ • Expense ratio / MER / TER: value                 │
│ • AUM / Net assets: value                          │
│ • Benchmark: value                                 │
│ • Risk rating / Riskometer: value                  │
│                                                    │
│ Source: Official source preferred                  │
│ Last updated from sources: date / fetch timestamp  │
└────────────────────────────────────────────────────┘
```

### Citation Display

Every answer must show:

- Primary source URL.
- Platform URL where available.
- Last updated from source or fetch timestamp.
- Source type: official / platform / PDF.
- Chunks used, optionally hidden under **View evidence**.

### Good Answer State

```text
The HDFC Pharma and Healthcare Fund is listed in the corpus as an India healthcare/pharma mutual fund. The available source includes fund details such as NAV, AUM, expense ratio, risk level, fund manager, and investment objective.

Source: https://groww.in/...
Last updated from sources: <source date or fetch timestamp>
```

### Missing Data State

Use a clear, non-apologetic state:

```text
I could not find this information in the current source set for this fund.
```

Add optional UI helper:

```text
Try asking about available fields such as expense ratio, AUM, benchmark, holdings, risk rating, or investment objective.
```

### Refusal State

For advice-seeking queries, show a distinct refusal card:

```text
I can't provide investment advice or buy/sell recommendations. I can help with factual details such as expense ratio, AUM, benchmark, holdings, risk rating, investment objective, and official source documents.
```

Visual treatment:

- Use neutral amber/gray tone, not red.
- Do not make it look like an error.
- Provide factual alternatives as chips.

---

## 6.3 Fund Explorer Screen

### Purpose

Let users browse the corpus without asking a question first.

### Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Filters: Country | Fund Type | Subcategory | Currency         │
├──────────────────────────────────────────────────────────────┤
│ Fund Card Grid                                               │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│ │ Fund A       │ │ Fund B       │ │ Fund C       │            │
│ └──────────────┘ └──────────────┘ └──────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

### Fund Card Fields

Each fund card should show only fields available in the corpus.

```text
Fund Name
Country / Market | Fund Type | Subcategory

Ticker / ISIN: value
Currency: value
Exchange: value
Expense ratio / MER / TER: value or Not found
AUM / Net Assets / Fund Size: value or Not found
Risk rating / Riskometer: value or Not found

[Ask about this fund] [Compare] [View sources]
```

### Fund Card Rules

- Do not show fake values.
- If a value is unavailable, show `Not found in corpus`.
- Do not show suitability phrases such as “good for aggressive investors.”
- Do not show “best”, “recommended”, or “top pick.”

---

## 6.4 Compare Funds Screen

### Purpose

Support factual side-by-side comparisons.

### Comparison Table

| Metric | Fund A | Fund B | Fund C |
|---|---|---|---|
| Country / Market | value | value | value |
| Fund type | value | value | value |
| Subcategory | value | value | value |
| Ticker / ISIN | value | value | value |
| Currency | value | value | value |
| Exchange | value | value | value |
| AUM / Net Assets / Fund Size | value | value | value |
| NAV / Market Price | value | value | value |
| Expense ratio / MER / TER | value | value | value |
| Benchmark | value | value | value |
| Risk rating / Riskometer | value | value | value |
| Fund house / issuer | value | value | value |
| Top holdings | value | value | value |
| Source | source chip | source chip | source chip |
| Last updated | date | date | date |

### Comparison Rules

Allowed comparison language:

```text
Among the selected funds, Fund A has the lowest available expense ratio in the current corpus.
```

Not allowed:

```text
Fund A is better.
Fund A is the best investment.
You should choose Fund A.
```

### Sort and Filter Controls

- Sort by factual fields only.
- Allow sorting by expense ratio, AUM, country, fund type, subcategory, or risk label.
- Do not enable “best fund” sorting unless the field is explicitly selected by the user.

### Export

For portfolio/demo value, support:

- Export comparison as CSV.
- Copy comparison table.
- Save comparison locally/session-only.

---

## 6.5 Fund Detail Page

### Purpose

Give a fund-level evidence-backed profile.

### Sections

#### 1. Fund Header

```text
Fund Name
Country / Market | Fund Type | Subcategory
Ticker / ISIN | Currency | Exchange
```

#### 2. Key Facts Grid

| Field | Display |
|---|---|
| NAV / Price | Value or Not found |
| AUM / Net Assets / Fund Size | Value or Not found |
| Expense Ratio / MER / TER | Value or Not found |
| Benchmark | Value or Not found |
| Risk Rating / Riskometer | Value or Not found |
| Fund House / Issuer | Value or Not found |
| Fund Manager | Value or Not found |

#### 3. Investment Objective

Show the official/retrieved objective text. Keep it concise and allow **View full extracted text**.

#### 4. Holdings and Exposure

Display only if retrieved:

- Top 10 holdings table.
- Sector exposure chart.
- Geographic exposure chart.

#### 5. Documents

Show:

- Factsheet.
- Prospectus.
- Fund Facts / ETF Facts.
- Platform page.
- Official page.

#### 6. Ask About This Fund

Provide pre-filled query chips:

- What is the expense ratio / MER / TER?
- What benchmark does this fund track?
- What are the top holdings?
- What is the investment objective?
- What is the risk rating?

---

## 6.6 Sources & Evidence Screen

### Purpose

Build RAG trust by making retrieval transparent.

### Source Table

| Fund | Country | Source Type | URL Type | Last Fetched | Status |
|---|---|---|---|---|---|
| XLV | USA | Official | Issuer | timestamp | Available |
| HDFC Pharma | India | Platform | Groww | timestamp | Available |
| Amova Asia Healthcare | Singapore | PDF | Factsheet | timestamp | Available |

### Evidence Drawer

When the user clicks **View evidence**, show:

```text
Retrieved chunk
Fund: XLV
Section: Expense ratio / MER / TER
Source type: Official
Source URL: ...
Last updated from source: ...
Fetch timestamp: ...
Extracted text: ...
```

### Source Reliability Labels

Use three labels:

| Label | Meaning |
|---|---|
| Official | Issuer, AMC, exchange, regulator, factsheet, prospectus |
| Platform | Groww, ETF.com, TMX, JustETF, Yahoo Finance, HKEX quote pages |
| PDF | Factsheet, Fund Facts, ETF Facts, prospectus |

Citation priority:

1. Official URL.
2. PDF factsheet / official document.
3. Platform URL.

---

## 7. Component System

## 7.1 Core Components

| Component | Purpose |
|---|---|
| `AppShell` | Main layout wrapper with sidebar, content, source panel |
| `TopBar` | Product name, disclaimer badge, refresh timestamp |
| `SidebarFilters` | Country, fund, type, subcategory filters |
| `QueryInput` | Chat input with example prompt chips |
| `AnswerCard` | Main RAG answer display |
| `FactChip` | Small field-value display with source marker |
| `SourceCard` | URL, source type, timestamp, used-for field |
| `EvidenceDrawer` | Expandable extracted chunk viewer |
| `FundCard` | Browseable fund summary |
| `ComparisonTable` | Side-by-side factual comparison |
| `DisclaimerBanner` | Facts-only/no-advice message |
| `RefusalCard` | Polite financial-advice refusal state |
| `MissingDataCard` | Missing field/corpus message |
| `LoadingRetrievalState` | Fetching/retrieving/generating progress |
| `EmptyState` | No selected fund/query state |

---

## 7.2 Answer Card Variants

### Factual Answer

Use for direct questions about a field.

Visual requirements:

- White card.
- Title: `Answer`.
- Concise text.
- Key facts grid if values exist.
- Source footer.
- Last updated footer.

### Comparison Answer

Use for country-wise or multi-fund comparisons.

Visual requirements:

- Short summary.
- Table first, explanation second.
- Missing values highlighted as `Not found`.
- Source count visible.

### Refusal Answer

Use for advice, prediction, portfolio, or personalized questions.

Visual requirements:

- Neutral card.
- No source link required.
- Suggested factual alternatives.

### Missing Data Answer

Use when the query is valid but corpus lacks the data.

Visual requirements:

- Light gray card.
- Exact missing-data message.
- Suggested available fields.

---

## 8. Visual Design System

## 8.1 Color Palette

Recommended trustworthy finance palette:

| Token | Suggested Value | Use |
|---|---:|---|
| `background` | `#F8FAFC` | App background |
| `surface` | `#FFFFFF` | Cards, panels |
| `surface-muted` | `#F1F5F9` | Secondary cards |
| `primary` | `#0F172A` | Headings, sidebar, primary text |
| `primary-accent` | `#1D4ED8` | Primary buttons, active filters |
| `trust-blue` | `#2563EB` | Source links, citation chips |
| `success` | `#15803D` | Positive factual status only |
| `warning` | `#B45309` | Refusal/advice boundary |
| `danger` | `#B91C1C` | Errors only, not market losses unless factual |
| `border` | `#E2E8F0` | Card/table borders |
| `text-muted` | `#64748B` | Metadata, timestamps |

### Important Color Rule

Do not overuse green/red for investment interpretation. Use green/red only for literal factual values or UI states. Avoid visually implying “good” or “bad” fund quality.

---

## 8.2 Typography

Recommended:

| Use | Style |
|---|---|
| Font family | Inter, IBM Plex Sans, or system sans-serif |
| Page title | 28-32px, 700 weight |
| Section title | 18-22px, 600 weight |
| Card title | 15-16px, 600 weight |
| Body | 14-16px, 400 weight |
| Metadata | 12-13px, 400 weight |
| Table cell | 13-14px |

Typography should feel professional and compact, similar to analytics dashboards.

---

## 8.3 Spacing

Use an 8px spacing system:

| Token | Size |
|---|---:|
| `space-1` | 4px |
| `space-2` | 8px |
| `space-3` | 12px |
| `space-4` | 16px |
| `space-6` | 24px |
| `space-8` | 32px |
| `space-12` | 48px |

Cards should be compact but not crowded. Finance users need scanability.

---

## 8.4 Border Radius and Shadows

| Element | Radius | Shadow |
|---|---:|---|
| Main cards | 12px | subtle |
| Chips | 999px | none |
| Tables | 10px | none / subtle border |
| Buttons | 8px | none |
| Modals/drawers | 16px | medium |

Use borders more than heavy shadows. This keeps the product professional.

---

## 9. Interaction Design

## 9.1 Query Flow

```text
User enters factual query
↓
UI sends query + filters to backend
↓
Guardrail classifier checks intent
↓
If factual/comparison: retrieval runs
↓
Answer generated from chunks
↓
Answer card + sources panel update
↓
User can inspect evidence or ask follow-up
```

## 9.2 Loading States

Show meaningful progress:

```text
Classifying query...
Retrieving relevant fund facts...
Checking source evidence...
Generating cited answer...
```

Do not show fake progress percentages.

## 9.3 Source Panel Interaction

The right-side source panel should update every time a response is generated.

Source card actions:

- Open original link.
- View extracted text.
- Show metadata.
- Copy source URL.

## 9.4 Follow-Up Suggestions

Show only factual follow-ups, such as:

- Show the benchmark.
- Show the expense ratio / MER / TER.
- Show top holdings.
- Compare AUM across selected funds.
- Show funds available country-wise.

Do not suggest:

- Should I invest?
- Which is best for me?
- What should I buy?

---

## 10. Guardrail UX Design

Guardrails should be visible but not annoying.

### 10.1 Advice Query State

When the backend classifies a query as `ADVICE`, display:

```text
I can't provide investment advice or buy/sell recommendations. I can help with factual details such as expense ratio, AUM, benchmark, holdings, risk rating, investment objective, and official source documents.
```

Show factual chips:

- Compare expense ratios.
- Show AUM.
- Show benchmark.
- Show holdings.
- Show risk rating.

### 10.2 Out-of-Scope State

```text
This assistant only covers healthcare, pharma, biotech, med-tech, and healthcare innovation funds across the supported markets. Try asking about a fund, country, benchmark, holdings, expense ratio, AUM, or source document.
```

### 10.3 PII State

If user enters PAN, Aadhaar, account numbers, OTP, phone, broker credentials, or private portfolio details:

```text
Please do not share personal or financial account information. This assistant only uses public fund sources and cannot process private account or portfolio data.
```

---

## 11. Data-Aware UI Mapping

The frontend should map API response fields directly to UI components.

### ChatResponse → UI

| API Field | UI Display |
|---|---|
| `answer` | AnswerCard body |
| `source_url` | Primary SourceCard link |
| `platform_url` | Secondary platform link |
| `last_updated` | Source timestamp |
| `fetch_timestamp` | Corpus refresh metadata |
| `is_refusal` | RefusalCard variant |
| `intent` | Debug badge / hidden metadata |
| `missing_data` | MissingDataCard variant |
| `chunks_used` | EvidenceDrawer |

### Fund Fields → FundCard

| Normalized Field | UI Label |
|---|---|
| `fund_name` | Fund name |
| `country_or_market` | Country / Market |
| `ticker_or_identifier` | Ticker / ISIN |
| `fund_type` | Fund Type |
| `domain_subcategory` | Subcategory |
| `nav_or_price` | NAV / Price |
| `aum` | AUM / Net Assets / Fund Size |
| `expense_ratio_or_mer_or_ter` | Expense Ratio / MER / TER |
| `benchmark` | Benchmark |
| `risk_rating_or_riskometer` | Risk Rating / Riskometer |
| `fund_house_or_issuer` | Fund House / Issuer |
| `top_10_holdings` | Top Holdings |
| `source_url` | Source |
| `last_updated_from_source` | Last Updated |

---

## 12. MVP Implementation in Streamlit

The current architecture references Streamlit as the frontend. For MVP, implement the design as follows.

### 12.1 Streamlit Page Structure

```python
st.set_page_config(
    page_title="FinanceBot Research Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
country = st.sidebar.selectbox("Country / Market", [...])
fund = st.sidebar.selectbox("Fund", [...])
subcategory = st.sidebar.multiselect("Subcategory", [...])

# Main tabs
tab_chat, tab_explorer, tab_compare, tab_sources = st.tabs([
    "Ask AI",
    "Fund Explorer",
    "Compare Funds",
    "Sources"
])
```

### 12.2 Streamlit Layout

Use three columns for chat screen:

```python
left, main, right = st.columns([0.22, 0.53, 0.25])
```

Or use sidebar + two main columns:

```python
main, sources = st.columns([0.68, 0.32])
```

### 12.3 Streamlit MVP Components

| UI Need | Streamlit Component |
|---|---|
| Filters | `st.sidebar.selectbox`, `st.sidebar.multiselect` |
| Query input | `st.chat_input` or `st.text_input` |
| Answer | `st.container`, `st.markdown` |
| Sources | `st.expander`, `st.link_button` |
| Comparison | `st.dataframe` |
| Charts | `st.bar_chart` or Plotly/ECharts extension |
| Disclaimer | `st.info` |
| Refusal | `st.warning` |
| Missing data | `st.caption` + neutral card |

### 12.4 MVP Styling

Add a custom `styles.css` file for:

- Card containers.
- Source chips.
- Disclaimer banner.
- Compact tables.
- Sidebar density.

---

## 13. Portfolio-Grade React Version

For a stronger portfolio presentation, build a frontend using:

| Layer | Tool |
|---|---|
| Framework | Next.js or Vite React |
| Styling | Tailwind CSS |
| Components | shadcn/ui |
| Tables | TanStack Table |
| Charts | Recharts or Apache ECharts |
| Icons | Lucide React |
| Animation | Motion.dev |
| API client | fetch / TanStack Query |
| State | Zustand or React state |

### Recommended React Routes

```text
/
/research
/funds
/funds/:fundId
/compare
/sources
/methodology
```

### Recommended React Components

```text
components/
├── layout/
│   ├── AppShell.tsx
│   ├── Sidebar.tsx
│   ├── TopBar.tsx
│   └── SourcePanel.tsx
├── chat/
│   ├── QueryInput.tsx
│   ├── AnswerCard.tsx
│   ├── RefusalCard.tsx
│   ├── MissingDataCard.tsx
│   └── FollowUpChips.tsx
├── funds/
│   ├── FundCard.tsx
│   ├── FundFactsGrid.tsx
│   ├── FundDetailHeader.tsx
│   └── HoldingsTable.tsx
├── compare/
│   ├── ComparisonTable.tsx
│   └── ComparisonToolbar.tsx
├── sources/
│   ├── SourceCard.tsx
│   ├── EvidenceDrawer.tsx
│   └── SourceStatusBadge.tsx
└── common/
    ├── DisclaimerBanner.tsx
    ├── EmptyState.tsx
    ├── LoadingState.tsx
    └── MetricChip.tsx
```

---

## 14. Motion and Animation Guidelines

Use animation only to improve clarity.

### Recommended Animations

| Interaction | Animation |
|---|---|
| Answer appears | Fade in + slight upward movement |
| Source panel opens | Slide from right |
| Evidence drawer expands | Smooth height expansion |
| Fund card hover | Slight border accent / shadow |
| Filter changes | Skeleton loading, not flashy spinner |
| Comparison table update | Subtle row fade |

### Avoid

- Crypto-style glowing charts.
- Excessive number counters.
- Fast transitions.
- Gamified recommendation effects.
- Confetti or “best fund” badges.

Motion should make the product feel trustworthy, not promotional.

---

## 15. Chart Guidelines

Charts should be used only for factual corpus data.

### Allowed Charts

| Chart | Use |
|---|---|
| Bar chart | Expense ratio / MER / TER comparison |
| Bar chart | AUM / fund size comparison |
| Donut chart | Sector exposure if available |
| Donut chart | Geographic exposure if available |
| Count chart | Funds by country or subcategory |
| Table-first view | Benchmark, issuer, risk rating comparisons |

### Conditional / V2 Charts

Performance charts are allowed only if factual historical return data is explicitly ingested and sourced. Until then, avoid:

- 1Y/3Y/5Y return charts.
- Performance ranking.
- Risk-return scatter plots.
- Prediction charts.

### Chart Footer

Every chart should include:

```text
Source: [source name]
Last updated from sources: [date]
```

---

## 16. Accessibility Requirements

- Minimum text contrast should meet WCAG AA.
- Do not rely only on color for risk/source status.
- All source chips should be keyboard accessible.
- Tables should have clear headers.
- Buttons should have visible focus states.
- Use semantic labels for filters and inputs.
- Expanders/drawers should be accessible through keyboard navigation.

---

## 17. Trust and Compliance Requirements

### Always Visible

- Facts-only disclaimer.
- Source link in every factual answer.
- Last updated / fetch timestamp where available.
- Missing-data state.

### Never Display

- “Recommended fund.”
- “Best fund for you.”
- “Buy now.”
- “Expected return.”
- “Suitable for your profile.”
- “Guaranteed.”
- “Low-risk investment” unless the exact risk label exists in the source.

### Language Rules

Use:

```text
The corpus shows...
The retrieved source states...
The available data includes...
Among the selected funds, the lowest available expense ratio is...
```

Avoid:

```text
You should invest...
This is better...
This will perform...
This is safe...
This is ideal for you...
```

---

## 18. Empty, Error, and Edge States

### Empty Chat State

```text
Ask a factual question about healthcare, pharma, biotech, or med-tech funds.
```

### No Matching Fund

```text
No matching fund was found in the current corpus. Try changing the country or removing filters.
```

### Source Fetch Failed

```text
This source could not be refreshed during the latest ingestion run. The system may use the last available extracted content if present.
```

### Comparison With Missing Values

```text
Some selected funds do not publish this field in the current source set. Missing values are shown as Not found.
```

### Advice Query

```text
I can't provide investment advice or buy/sell recommendations. I can help with factual details such as expense ratio, AUM, benchmark, holdings, risk rating, investment objective, and official source documents.
```

---

## 19. Recommended MVP Build Order

### Phase 1 — Functional MVP

1. Build Streamlit app shell.
2. Add sidebar filters.
3. Add query input.
4. Connect `/chat` API.
5. Display answer card.
6. Display source card.
7. Display disclaimer.
8. Display refusal/missing-data states.

### Phase 2 — Research Workspace

1. Add Fund Explorer.
2. Add Fund Detail view.
3. Add Compare Funds table.
4. Add evidence drawer.
5. Add source status table.

### Phase 3 — Portfolio Polish

1. Improve visual theme.
2. Add citation chips.
3. Add subtle Motion.dev animations.
4. Add export CSV.
5. Add source inspection drawer.
6. Add methodology page.

### Phase 4 — Advanced Version

1. Add React frontend.
2. Add persisted saved comparisons.
3. Add better charting.
4. Add multi-sector expansion.
5. Add v2 return/performance views only if sourced data exists.

---

## 20. Final Suggested Design

The strongest design for this project is:

> **Carbon-style analytics dashboard + Perplexity-style cited answers + Groww-style fund cards + Morningstar-style factual comparison.**

The MVP can be built in Streamlit, but the portfolio-grade version should use React, Tailwind, shadcn/ui, TanStack Table, Recharts/ECharts, and Motion.dev.

The most important product decision is to keep the interface evidence-first:

1. Ask a question.
2. Show factual answer.
3. Show normalized fund facts.
4. Show source links.
5. Show last updated timestamps.
6. Allow comparison only on corpus-backed fields.
7. Refuse advice clearly.

This will make FinanceBot feel like a credible financial research tool rather than a generic chatbot wrapper.
