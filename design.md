# HealthFundIQ — Design Specification

**Ask. Compare. Verify global healthcare funds — with facts, not financial advice.**

---

## 0. Product Identity

| Field | Value |
|---|---|
| App Name | HealthFundIQ |
| Tagline | Ask. Compare. Verify global healthcare funds — with facts, not financial advice. |
| Product Type | AI-powered cited financial research workspace |
| Domain | Healthcare / Pharma / Biotech / Med-Tech / Healthcare Innovation funds |
| Markets | India · USA · Canada · China/HK · Japan · Singapore · UK/Europe |
| Design Direction | Carbon-style analytics dashboard + Perplexity-style cited answers + Groww-style fund cards + Morningstar-style factual comparison |
| Core Principle | Evidence-first. Every answer, fact, and comparison traces back to a named public source. |
| MVP Frontend | Streamlit |
| Portfolio Frontend | React + Next.js + shadcn/ui + Tailwind CSS |

---

## 1. Design Philosophy

HealthFundIQ is not a chatbot wrapper. It is a **cited financial research terminal** for public healthcare fund data.

Three forces shape every design decision:

**1. Trust requires transparency.**
Every displayed fact carries a source label, a URL, and a fetch timestamp. Users can trace any value back to its origin. This is the product's core differentiator.

**2. Safety requires restraint.**
The UI must never imply recommendation, prediction, or advice. Colors, language, layout, and interaction patterns are all chosen to signal that this is a research tool, not an investment advisor.

**3. Clarity requires structure.**
Fund data from 7 markets uses different terminology, different field names, and different standards. The UI must normalize this into a consistent vocabulary the user can scan and compare without confusion.

---

## 2. App Name and Wordmark

### 2.1 Primary Name

```
HealthFundIQ
```

No spaces. No hyphen. Capital H, F, I, Q. The suffix IQ signals intelligence and research depth.

### 2.2 Tagline (full)

```
Ask. Compare. Verify global healthcare funds — with facts, not financial advice.
```

The three words Ask, Compare, Verify map exactly to the three primary screens:
- Ask → AI Research Chat
- Compare → Compare Funds
- Verify → Sources & Evidence

Use the tagline in:
- The welcome/home screen hero section.
- The top bar subtitle on desktop.
- The About / Methodology page.
- Any marketing or portfolio description of the project.

### 2.3 Names to Avoid

Never use in the product:
- Best Fund AI
- Investment Advisor Bot
- Portfolio Recommender
- Healthcare Fund Picker
- WealthGPT
- SmartFund

These names create advice expectations inconsistent with the project scope.

---

## 3. Information Architecture

### 3.1 Navigation Structure

```
HealthFundIQ
├── Ask AI              ← natural-language factual Q&A with citations
├── Fund Explorer       ← browse all corpus funds with filters
├── Compare Funds       ← side-by-side factual comparison table
├── Sources & Evidence  ← corpus status, source inspector, evidence drawer
└── About               ← methodology, disclaimer, scope
```

For Streamlit MVP: tabs at the top of the main content area.
For React version: left sidebar navigation with route-based pages.

### 3.2 Filter Hierarchy

Filters apply globally across all screens:

```
Country / Market       (All Countries | India | USA | Canada | China/HK | Japan | Singapore | UK/Europe)
    └── Fund            (dynamic list based on country selection)
         └── Subcategory (Pharma | Broad Healthcare | Biotech | Med-Tech | Healthcare Innovation)
              └── Fund Type (Mutual Fund | ETF | UCITS ETF | Fund | Index)
```

---

## 4. Layout System

### 4.1 Desktop Three-Panel Layout

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  TOP BAR                                                                      │
│  HealthFundIQ  |  Ask. Compare. Verify.  |  Last corpus refresh: timestamp   │
│  [Facts only. No investment advice.]                                          │
├────────────────┬──────────────────────────────────────────┬───────────────────┤
│  LEFT SIDEBAR  │  MAIN WORKSPACE                          │  SOURCE PANEL     │
│  (22%)         │  (53%)                                   │  (25%)            │
│                │                                          │                   │
│  Country       │  [Screen content renders here]           │  Sources used     │
│  Fund          │                                          │  ─────────────    │
│  Subcategory   │                                          │  Source card 1    │
│  Fund Type     │                                          │  Source card 2    │
│                │                                          │  Source card N    │
│  ─────────     │                                          │                   │
│  Example Qs    │                                          │  Evidence drawer  │
│                │                                          │  [View extracted] │
│  ─────────     │                                          │                   │
│  About         │                                          │  Corpus health    │
│  Methodology   │                                          │  Last refreshed   │
└────────────────┴──────────────────────────────────────────┴───────────────────┘
```

### 4.2 Mobile Stacked Layout

```
┌────────────────────────────┐
│  TOP BAR + Menu            │
├────────────────────────────┤
│  Query input               │
├────────────────────────────┤
│  Filters accordion         │
├────────────────────────────┤
│  Answer card               │
├────────────────────────────┤
│  Fact chips                │
├────────────────────────────┤
│  Sources (collapsible)     │
├────────────────────────────┤
│  Disclaimer footer         │
└────────────────────────────┘
```

### 4.3 Column Grid

Use a 12-column grid:
- Left sidebar: 3 columns
- Main content: 6 columns
- Source panel: 3 columns
- On mobile: all 12 columns stacked

---

## 5. Color Palette

### 5.1 Primary Palette

| Token | Hex | Use |
|---|---|---|
| `background` | `#F8FAFC` | App shell background |
| `surface` | `#FFFFFF` | Cards, panels, answer containers |
| `surface-muted` | `#F1F5F9` | Secondary cards, source panel background, alternate table rows |
| `surface-dark` | `#0F172A` | Top bar, sidebar (dark mode option) |
| `border` | `#E2E8F0` | All card borders, table dividers |
| `border-strong` | `#CBD5E1` | Active filter, focused input |

### 5.2 Brand and Interactive

| Token | Hex | Use |
|---|---|---|
| `primary` | `#0F172A` | Headings, sidebar text, body text |
| `primary-accent` | `#1D4ED8` | Primary buttons, active filter pills, nav highlights |
| `trust-blue` | `#2563EB` | All source links and citation chips |
| `trust-blue-light` | `#EFF6FF` | Source chip background |
| `brand-teal` | `#0D9488` | HealthFundIQ wordmark accent; secondary brand touch |

### 5.3 Status and State

| Token | Hex | Use |
|---|---|---|
| `official-green` | `#15803D` | "Official" source badge |
| `platform-slate` | `#475569` | "Platform" source badge |
| `pdf-amber` | `#B45309` | "PDF" source badge |
| `refusal-amber` | `#92400E` | Refusal card text |
| `refusal-bg` | `#FFFBEB` | Refusal card background |
| `missing-gray` | `#64748B` | Missing data text |
| `missing-bg` | `#F8FAFC` | Missing data card background |
| `error-red` | `#B91C1C` | System errors only (fetch failures) |

### 5.4 Critical Color Rules

**Do not use green/red for market performance.** These colors are reserved only for source status (official = green badge) and system errors. Never use them to imply a fund is performing well or poorly.

**Do not use "hot" finance colors** (neon green, flashing red) that suggest trading or urgency. HealthFundIQ is a research tool, not a trading terminal.

**Expense ratio comparisons** should use a neutral bar chart, not traffic-light coloring, because a lower expense ratio does not automatically mean "good" — it depends on context the bot cannot provide.

---

## 6. Typography

### 6.1 Font Stack

```
Primary font: Inter
Fallback: IBM Plex Sans, system-ui, sans-serif
Monospace (for fund codes, ISINs, tickers): JetBrains Mono, Fira Code, monospace
```

### 6.2 Type Scale

| Role | Size | Weight | Usage |
|---|---|---|---|
| App name (wordmark) | 22px | 700 | Top bar |
| Page / screen title | 28–32px | 700 | Welcome hero, screen headings |
| Section heading | 18–22px | 600 | Card section titles |
| Card title | 15–16px | 600 | Answer card title, fund card name |
| Body text | 14–16px | 400 | Answer text, paragraph content |
| Label / field name | 13px | 500 | Field labels in fact grids |
| Value / data | 14px | 400–600 | Field values in fact grids |
| Metadata / timestamp | 12px | 400 | Source dates, fetch timestamps |
| Table cell | 13–14px | 400 | Comparison table content |
| Chip / badge | 11–12px | 500 | Source badges, filter chips |
| Code / ticker | 13px | 400 (mono) | Ticker symbols, ISINs, URLs |

---

## 7. Spacing and Layout Tokens

Use an 8px base spacing system.

| Token | Value |
|---|---|
| `space-1` | 4px |
| `space-2` | 8px |
| `space-3` | 12px |
| `space-4` | 16px |
| `space-6` | 24px |
| `space-8` | 32px |
| `space-12` | 48px |
| `space-16` | 64px |

### Border Radius

| Element | Radius |
|---|---|
| Cards (main) | 12px |
| Source cards | 10px |
| Filter chips / badges | 999px (fully rounded) |
| Buttons (primary) | 8px |
| Input fields | 8px |
| Tables | 10px outer, 0 cell |
| Modals / drawers | 16px |
| Fact chip | 6px |

### Shadow

| Element | Shadow |
|---|---|
| Main content card | `0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)` |
| Sidebar | none (bordered) |
| Source panel | `0 2px 6px rgba(0,0,0,0.06)` |
| Drawer / modal | `0 8px 30px rgba(0,0,0,0.12)` |
| Hover state (fund card) | `0 4px 12px rgba(0,0,0,0.08)` |

Prefer borders over heavy shadows. The product should feel like a clean data tool, not a consumer app.

---

## 8. Screen-Level Design

### 8.1 Home / Welcome Screen

**Purpose:** Introduce HealthFundIQ, set expectations, guide toward factual questions.

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   HealthFundIQ                                                  │
│   Ask. Compare. Verify global healthcare funds —                │
│   with facts, not financial advice.                             │
│                                                                 │
│   ─────────────────────────────────────────────────────────    │
│   [   Ask a factual question about a healthcare fund...   ] [→] │
│   ─────────────────────────────────────────────────────────    │
│                                                                 │
│   Example questions:                                            │
│   [Expense ratio] [Canada funds] [XLV benchmark]               │
│   [Biotech funds] [Country-wise]  [Top holdings of IBB]        │
│                                                                 │
│   ────────────────────────────────────────────────────────     │
│   ⚠  Facts only. No investment advice. Always verify from      │
│      official fund documents before making financial decisions. │
│   ────────────────────────────────────────────────────────     │
│                                                                 │
│   Coverage: India · USA · Canada · China/HK · Japan ·          │
│             Singapore · UK/Europe                               │
│   Funds: ~34 healthcare/pharma/biotech/med-tech funds          │
│   Refreshed daily at 10:00 AM IST                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Hero Copy (exact text)

**Headline:**
```
Ask. Compare. Verify.
Global healthcare funds — with facts, not financial advice.
```

**Subheadline:**
```
HealthFundIQ retrieves and presents factual information about healthcare, pharma, biotech, and med-tech funds across India, USA, Canada, China/Hong Kong, Singapore, Japan, and the UK from public sources. Every answer cites its source.
```

#### Example Prompt Chips

| Chip label | Full query inserted |
|---|---|
| Expense ratio | What is the expense ratio of HDFC Pharma and Healthcare Fund? |
| Canada funds | Which healthcare ETFs are available in Canada? |
| XLV benchmark | What benchmark does XLV track? |
| Biotech focus | Which funds in this corpus are biotech-focused? |
| Country-wise | Show healthcare funds available country-wise. |
| IBB holdings | What are the top holdings of IBB? |
| VHT objective | What is the investment objective of VHT? |

Clicking a chip navigates to Ask AI and pre-fills the query input.

#### Coverage Strip (below input)

```
7 markets · ~34 funds · Facts only · Refreshed daily
India ○ USA ○ Canada ○ China/HK ○ Japan ○ Singapore ○ UK/Europe
```

---

### 8.2 Ask AI Screen

**Purpose:** Natural-language factual Q&A with full source citation.

#### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  Ask AI — Factual fund research                                  │
├──────────────────────────────────────┬───────────────────────────┤
│  MAIN AREA (68%)                     │  SOURCE PANEL (32%)       │
│                                      │                           │
│  [Query input]                       │  Sources used             │
│                                      │  ─────────────────────    │
│  ─────── Chat history ────────       │  ┌─────────────────────┐  │
│                                      │  │ [Official] XLV       │  │
│  User: What is the expense ratio     │  │ ssga.com/...         │  │
│  of XLV?                             │  │ Last updated: Jun 1  │  │
│                                      │  │ Fetched: Jun 2 10:00 │  │
│  ┌────────────────────────────────┐  │  │ [View extracted text]│  │
│  │ Answer                         │  │  └─────────────────────┘  │
│  │                                │  │                           │
│  │ The expense ratio of the        │  │  ┌─────────────────────┐  │
│  │ Health Care Select Sector       │  │  │ [Platform] ETF.com   │  │
│  │ SPDR ETF (XLV) is 0.09%.        │  │  │ etf.com/XLV          │  │
│  │                                │  │  │ Also see             │  │
│  │ Key facts                       │  │  └─────────────────────┘  │
│  │ • Expense ratio: 0.09%          │  │                           │
│  │ • Issuer: SSGA                  │  │  Corpus health            │
│  │ • Exchange: NYSE Arca           │  │  ─────────────────────    │
│  │                                │  │  USA: 5/5 sources OK      │
│  │ Source: ssga.com/...            │  │  Last run: Jun 2 10:00 AM │
│  │ Last updated: 2026-06-01        │  └───────────────────────────┘
│  └────────────────────────────────┘
│                                      │
│  Follow-up questions:                │
│  [Show holdings of XLV]             │
│  [What is VHT expense ratio?]       │
│  [Show all US healthcare ETFs]      │
│                                      │
│  ─────────────────────────────────  │
│  [  Ask about healthcare funds...  ] [→]
└──────────────────────────────────────┘
```

#### Query Input

- Full-width input field.
- Placeholder: `Ask about expense ratio, AUM, benchmark, holdings, risk rating, issuer, or investment objective...`
- Submit with Enter or → button.
- Character limit: 500 (matches API validation).

#### Answer Card — Variants

**Variant 1: Factual answer**

```
┌──────────────────────────────────────────────────────┐
│  Answer                                              │
│                                                      │
│  [Concise factual text, 2–5 sentences max]           │
│                                                      │
│  Key facts                                           │
│  ┌─────────────────────┬──────────────────────────┐  │
│  │ Expense ratio / MER │ 0.09%                    │  │
│  │ AUM / Net Assets    │ USD 42.1B                │  │
│  │ Benchmark           │ Health Care Select Index  │  │
│  │ Issuer              │ State Street (SSGA)      │  │
│  └─────────────────────┴──────────────────────────┘  │
│                                                      │
│  Source [Official]  ssga.com/xlv  ↗                  │
│  Also see: etf.com/XLV  ↗                            │
│  Last updated from sources: 2026-06-01               │
│  Fetched by HealthFundIQ: 2026-06-02 10:00 AM IST    │
└──────────────────────────────────────────────────────┘
```

**Variant 2: Comparison answer**

```
┌──────────────────────────────────────────────────────┐
│  Comparison                                          │
│                                                      │
│  [Short summary text]                                │
│                                                      │
│  ┌──────────────┬────────┬────────┬────────────────┐  │
│  │ Field        │ XLV    │ VHT    │ IBB            │  │
│  ├──────────────┼────────┼────────┼────────────────┤  │
│  │ Country      │ USA    │ USA    │ USA            │  │
│  │ Expense ratio│ 0.09%  │ 0.10%  │ 0.44%          │  │
│  │ AUM          │ $42B   │ $18B   │ $8B            │  │
│  │ Benchmark    │ HC Sel │ MSCI   │ Nasdaq Bio      │  │
│  └──────────────┴────────┴────────┴────────────────┘  │
│                                                      │
│  Sources: ssga.com, vanguard.com, ishares.com        │
│  Last updated: 2026-06-01                            │
└──────────────────────────────────────────────────────┘
```

**Variant 3: Refusal answer**

```
┌──────────────────────────────────────────────────────┐
│  ⚠  This is outside what HealthFundIQ can answer     │
│                                                      │
│  I can't provide investment advice or buy/sell        │
│  recommendations. I can help with factual details     │
│  such as expense ratio, AUM, benchmark, holdings,    │
│  risk rating, investment objective, and official     │
│  source documents.                                   │
│                                                      │
│  Instead, try asking:                                │
│  [What is the expense ratio?]  [Show AUM]            │
│  [What benchmark does it track?]  [Show holdings]    │
└──────────────────────────────────────────────────────┘
```

Visual: amber/warm background (`#FFFBEB`), amber text. Not red — this is not an error, it is a scope boundary.

**Variant 4: Missing data**

```
┌──────────────────────────────────────────────────────┐
│  I could not find this information in the current    │
│  source set for this fund.                           │
│                                                      │
│  Available fields for this fund:                     │
│  expense ratio · benchmark · fund house · objective  │
│                                                      │
│  Try asking about one of those fields instead.       │
└──────────────────────────────────────────────────────┘
```

Visual: light gray background (`#F8FAFC`), muted text. No alarming color.

#### Fact Chip (inline with answer)

```
┌─────────────────────────────────┐
│  Expense Ratio / MER / TER      │
│  0.09%                          │
│  Source [Official] ↗            │
└─────────────────────────────────┘
```

Small, scannable, always carries a source label.

#### Follow-Up Question Chips

Generated by the LLM or hardcoded per section type. Show 3–5 max. Only factual suggestions:

```
[Show top holdings of XLV]
[What is the benchmark of VHT?]
[Compare XLV vs VHT expense ratio]
[Which US healthcare ETFs are in the corpus?]
```

Never suggest:
- "Should I invest in XLV?"
- "Is XLV good for me?"
- "Which US healthcare ETF will perform better?"

#### Loading States (sequential, not fake percentages)

```
Classifying query...
Retrieving relevant fund facts...
Checking source evidence...
Generating cited answer...
```

Show each step with a subtle progress indicator. Total expected time: 1–3 seconds.

---

### 8.3 Fund Explorer Screen

**Purpose:** Browse all corpus funds without asking a question.

#### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  Fund Explorer — 34 healthcare funds across 7 markets            │
│                                                                  │
│  Filter:  [Country ▼]  [Type ▼]  [Subcategory ▼]  [Clear]       │
│                                                                  │
│  Showing: 5 India funds | Mutual Fund | Pharma / Broad Healthcare│
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │ HDFC Pharma Fund     │  │ Nippon India Pharma  │               │
│  │ India · Mutual Fund  │  │ India · Mutual Fund  │               │
│  │ Pharma / Healthcare  │  │ Pharma               │               │
│  │ ─────────────────   │  │ ─────────────────    │               │
│  │ Expense ratio: 0.67% │  │ Expense ratio: 0.63% │               │
│  │ AUM: INR 5,234 Cr    │  │ AUM: INR 8,142 Cr    │               │
│  │ Risk: Very High      │  │ Risk: Very High      │               │
│  │ Benchmark: Nifty HC  │  │ Benchmark: Nifty 500 │               │
│  │ ─────────────────   │  │ ─────────────────    │               │
│  │ [Ask] [Compare] [→] │  │ [Ask] [Compare] [→]  │               │
│  └─────────────────────┘  └─────────────────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

#### Fund Card Specification

```
┌──────────────────────────────────────────────┐
│  Fund Name (full official name)              │
│  Country / Market · Fund Type · Subcategory  │
│                                              │
│  Ticker: XLV    ISIN: —    Currency: USD     │
│  Exchange: NYSE Arca                         │
│  ──────────────────────────────────────────  │
│  Expense Ratio / MER / TER   0.09%           │
│  AUM / Net Assets / Fund Size  USD 42.1B     │
│  Risk Rating / Riskometer    —               │
│  Benchmark                   Health Care SI  │
│  Fund House / Issuer         SSGA            │
│  ──────────────────────────────────────────  │
│  Source [Official]  ssga.com/xlv             │
│  Last updated: 2026-06-01                    │
│  ──────────────────────────────────────────  │
│  [Ask about this fund]  [+ Compare]  [→]     │
└──────────────────────────────────────────────┘
```

**Fund Card Rules:**
- If a field is unavailable: show `Not found in corpus` in muted text.
- Never show fake placeholder values.
- Never add editorial labels like "aggressive", "safe", "good for beginners."
- Never show "Top Pick", "Recommended", "Best in class."

#### Country Group Header

When no country filter is applied, group fund cards by country with a header row:

```
─── India (5 funds) ─────────────────────────────
[HDFC Pharma] [Nippon India] [Mirae] [SBI HC] [ICICI PHD]

─── USA (5 funds) ───────────────────────────────
[XLV] [VHT] [IXJ] [IBB] [FHLC]
```

---

### 8.4 Compare Funds Screen

**Purpose:** Side-by-side factual comparison of selected funds.

#### Fund Selector

Users pick up to 5 funds:

```
Selected funds: [XLV ×]  [VHT ×]  [HHL ×]  [+ Add fund]
```

Add fund via search by name, ticker, or country filter.

#### Comparison Table

```
┌─────────────────────┬──────────────────┬──────────────────┬────────────────────┐
│ Field               │ XLV              │ VHT              │ HHL                │
├─────────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ Country / Market    │ USA              │ USA              │ Canada             │
│ Fund Type           │ ETF              │ ETF              │ ETF                │
│ Subcategory         │ Broad Healthcare │ Broad Healthcare │ Broad Healthcare   │
│ Ticker / ISIN       │ XLV              │ VHT              │ HHL                │
│ Currency            │ USD              │ USD              │ CAD                │
│ Exchange            │ NYSE Arca        │ NYSE Arca        │ TSX                │
│ AUM / Net Assets    │ USD 42.1B        │ USD 18.3B        │ CAD 621M           │
│ NAV / Price         │ USD 148.72       │ USD 262.14       │ CAD 10.24          │
│ Expense Ratio/MER   │ 0.09%            │ 0.10%            │ 0.85% (MER)        │
│ Benchmark           │ Health Care Sel. │ MSCI US HC 25/50 │ Solactive HC Lead. │
│ Risk                │ —                │ —                │ Medium             │
│ Fund House / Issuer │ SSGA             │ Vanguard         │ Harvest Portfolios │
│ Top Holdings (1)    │ UNH 12.4%        │ UNH 13.1%        │ UNH 10.2%          │
│ Source              │ [Official] ↗     │ [Official] ↗     │ [Official] ↗       │
│ Last Updated        │ 2026-06-01       │ 2026-06-01       │ 2026-05-30         │
└─────────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

**Rendering rules:**
- Missing values → `Not found` in `color: #94A3B8` muted gray.
- Currency displayed alongside every monetary value. No implicit conversion.
- Source chip per fund at the bottom of each column.
- Sort by column allowed for: expense ratio, AUM, country, fund type.

**Comparison language rules:**

Allowed:
```
Among the selected funds, XLV has the lowest available expense ratio (0.09%) in the current corpus.
```

Not allowed:
```
XLV is better.
XLV is the best fund.
You should choose XLV.
HHL is riskier.
```

#### Export Controls

```
[Export as CSV]  [Copy table]  [Clear comparison]
```

CSV export includes: fund_name, country, fund_type, expense_ratio, aum, benchmark, risk, source_url, last_updated, fetch_timestamp.

---

### 8.5 Fund Detail Page

**Purpose:** A full evidence-backed profile for a single fund.

#### URL Structure (React)
```
/funds/usa_xlv
/funds/india_hdfc_pharma
```

#### Page Layout

```
┌───────────────────────────────────────────────────────────────────┐
│  ← Back to Fund Explorer                                          │
│                                                                   │
│  Health Care Select Sector SPDR ETF                               │
│  USA · ETF · Broad Healthcare · XLV · USD · NYSE Arca            │
│                                                                   │
│  [Ask about this fund]  [+ Compare]  [View sources]              │
├───────────────────────────────────────────────────────────────────┤
│  KEY FACTS                                                        │
│  ┌──────────────┬──────────────┬──────────────┬────────────────┐  │
│  │ NAV          │ AUM          │ Expense Ratio│ Benchmark      │  │
│  │ USD 148.72   │ USD 42.1B    │ 0.09%        │ Health Care    │  │
│  │              │              │              │ Select Sector  │  │
│  └──────────────┴──────────────┴──────────────┴────────────────┘  │
│  ┌──────────────┬──────────────┬──────────────┬────────────────┐  │
│  │ Fund House   │ Exchange     │ Currency     │ Risk Rating    │  │
│  │ SSGA         │ NYSE Arca    │ USD          │ Not found      │  │
│  └──────────────┴──────────────┴──────────────┴────────────────┘  │
├───────────────────────────────────────────────────────────────────┤
│  INVESTMENT OBJECTIVE                                             │
│  Seeks to provide investment results that, before expenses,       │
│  correspond generally to the price and yield performance of       │
│  the Health Care Select Sector Index.                             │
│  Source: ssga.com  Last updated: 2026-06-01                       │
├───────────────────────────────────────────────────────────────────┤
│  TOP 10 HOLDINGS              │  SECTOR EXPOSURE                  │
│  1. UnitedHealth Group 12.4%  │  Pharma 28.4%                    │
│  2. Eli Lilly           11.8%  │  HC Equipment 16.2%              │
│  3. J&J                  8.3%  │  Managed HC 15.9%                │
│  ...                          │  ...                              │
│  Source: ssga.com             │  Source: ssga.com                 │
├───────────────────────────────────────────────────────────────────┤
│  DOCUMENTS                                                        │
│  Factsheet: ssga.com/...     Prospectus: sec.gov/...             │
├───────────────────────────────────────────────────────────────────┤
│  ASK ABOUT THIS FUND                                              │
│  [Expense ratio?] [Benchmark?] [Top holdings?] [Objective?]      │
│  [Risk rating?]   [Fund manager?]                                 │
└───────────────────────────────────────────────────────────────────┘
```

---

### 8.6 Sources & Evidence Screen

**Purpose:** Make the RAG corpus fully transparent. Users can see every source, its status, and the extracted text.

#### Corpus Status Table

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Corpus Status — Last refreshed: 2026-06-02 10:00 AM IST                    │
├────────────────────┬────────────┬────────────┬──────────────┬────────────────┤
│ Fund               │ Country    │ Source Type│ Last Fetched │ Status         │
├────────────────────┼────────────┼────────────┼──────────────┼────────────────┤
│ XLV                │ USA        │ Official   │ 10:03 AM     │ ✓ Available    │
│ HDFC Pharma        │ India      │ Platform   │ 10:01 AM     │ ✓ Available    │
│ Amova Asia HC Fund │ Singapore  │ PDF        │ 10:07 AM     │ ✓ Available    │
│ 2820.HK (Yahoo)    │ China/HK   │ Platform   │ —            │ ✗ Failed (429) │
│ 1621.T             │ Japan      │ Platform   │ 10:09 AM     │ ✓ Available    │
└────────────────────┴────────────┴────────────┴──────────────┴────────────────┘
```

Status indicators:
- `✓ Available` — green check, fetched successfully this run.
- `⚠ Stale` — amber, last fetched > 24 hours ago.
- `✗ Failed` — red cross, with error code in tooltip.
- `📄 PDF` — PDF source badge.

#### Evidence Drawer

Triggered when user clicks "View extracted text" on a source card or answer.

```
┌─────────────────────────────────────────────────────────────────┐
│  Evidence — XLV · Expense Ratio / MER / TER                     │
│  ─────────────────────────────────────────────────────────────  │
│  Fund: Health Care Select Sector SPDR ETF                        │
│  Country: USA                                                   │
│  Section: cost_ratio                                             │
│  Source type: Official                                           │
│  Source URL: ssga.com/us/en/intermediary/etfs/...               │
│  Last updated from source: 2026-06-01                            │
│  Fetched by HealthFundIQ: 2026-06-02T10:03:41+05:30             │
│  ─────────────────────────────────────────────────────────────  │
│  Extracted text:                                                 │
│  [Health Care Select Sector SPDR ETF | USA | Expense Ratio]     │
│  The expense ratio (cost ratio) of XLV is 0.09%.               │
│  ─────────────────────────────────────────────────────────────  │
│  [Open original source ↗]  [Copy URL]  [Close ×]               │
└─────────────────────────────────────────────────────────────────┘
```

#### Source Reliability Labels

| Badge | Color | Meaning |
|---|---|---|
| `[Official]` | `#15803D` (green) | Issuer, AMC, exchange, regulator, factsheet, prospectus URL |
| `[Platform]` | `#475569` (slate) | Groww, ETF.com, TMX Money, JustETF, Yahoo Finance, HKEX |
| `[PDF]` | `#B45309` (amber) | Downloaded PDF factsheet, Fund Facts, ETF Facts |

Citation priority order (official → PDF → platform) is enforced in the backend and displayed visually in the source panel — official sources always appear first.

---

### 8.7 About / Methodology Page

**Purpose:** Explain what HealthFundIQ is, what it covers, and what it cannot do. Builds trust.

#### Sections

1. **What is HealthFundIQ?**
   — Facts-only RAG assistant for global healthcare funds.

2. **How does it work?**
   — Public source → ingestion → normalization → chunking → embedding → retrieval → cited answer.

3. **What markets does it cover?**
   — List all 7 markets with fund counts.

4. **What fields does it extract?**
   — List normalized fields.

5. **What is the difference between Official and Platform sources?**
   — Explain source type hierarchy.

6. **What can HealthFundIQ NOT do?**
   — Full out-of-scope list (investment advice, return prediction, portfolio building, personalized guidance, PII).

7. **How fresh is the data?**
   — Daily refresh at 10:00 AM IST. Fetch timestamps shown on every answer.

8. **Disclaimer (full text)**

```
HealthFundIQ provides factual information sourced from public fund pages,
official issuer documents, and publicly accessible financial data platforms.
It does not provide investment advice, buy/sell recommendations, portfolio
construction guidance, return predictions, or personalized financial guidance.

All information is sourced from public sources and may not reflect the most
current fund data. Always verify details from official fund documents and
consult a qualified financial adviser before making investment decisions.

HealthFundIQ is a research tool and information assistant only.
```

---

## 9. Component System

### 9.1 Core Component Inventory

| Component | Description | Used in |
|---|---|---|
| `AppShell` | Main layout wrapper: top bar, sidebar, content, source panel | All screens |
| `TopBar` | HealthFundIQ wordmark, tagline, last refresh timestamp, disclaimer badge | All screens |
| `SidebarFilters` | Country, fund, subcategory, type filters | All screens |
| `QueryInput` | Full-width query input with placeholder and submit | Ask AI, Home |
| `PromptChips` | Clickable example question chips | Home, Ask AI |
| `AnswerCard` | Main RAG answer container; supports 4 variants | Ask AI |
| `FactGrid` | 2-column field-value grid inside AnswerCard | Ask AI, Fund Detail |
| `FactChip` | Single field-value unit with source label | Ask AI, Fund Detail |
| `SourceCard` | URL + source type badge + timestamp + open link | Source panel |
| `EvidenceDrawer` | Expandable extracted chunk viewer | Sources screen, Source panel |
| `FundCard` | Browseable fund summary card | Fund Explorer |
| `FundHeader` | Fund name, country, type, ticker, ISIN strip | Fund Detail |
| `ComparisonTable` | Side-by-side factual comparison grid | Compare Funds |
| `ComparisonToolbar` | Fund selector, sort, export controls | Compare Funds |
| `CorpusStatusTable` | Per-fund ingestion status grid | Sources screen |
| `DisclaimerBanner` | Persistent facts-only/no-advice strip | All screens |
| `RefusalCard` | Amber refusal message with factual alternatives | Ask AI |
| `MissingDataCard` | Gray missing-data message with available fields | Ask AI |
| `LoadingState` | Sequential classified → retrieving → generating | Ask AI |
| `EmptyState` | Empty corpus query / no selected fund | Ask AI, Explorer |
| `SourceBadge` | `[Official]`, `[Platform]`, `[PDF]` colored pill | Everywhere |
| `CountryBadge` | India/USA/Canada/etc. labeled pill | Fund cards |
| `MetricChip` | Value display chip with label | Fact grid cells |
| `FollowUpChips` | Suggested factual follow-up questions | After answer |

### 9.2 AnswerCard Variants Summary

| Variant | Background | Border | Icon | Source shown |
|---|---|---|---|---|
| FACTUAL | `#FFFFFF` | `#E2E8F0` | None | Yes — always |
| COMPARISON | `#FFFFFF` | `#E2E8F0` | None | Yes — multiple |
| REFUSAL | `#FFFBEB` | `#FCD34D` | ⚠ | No |
| MISSING | `#F8FAFC` | `#E2E8F0` | — | No |

### 9.3 Source Panel — Content Priority

The source panel always shows:
1. Official source cards first.
2. PDF source cards second.
3. Platform source cards third.
4. Corpus health strip at the bottom (last refresh timestamp + any failed sources).

---

## 10. Interaction Design

### 10.1 Full Query Flow

```
User types query
        │
        ▼
Loading state begins
        │
        ▼
"Classifying query..." → intent detected
        │
        ├── ADVICE / OUT_OF_SCOPE
        │       └── RefusalCard rendered immediately (no retrieval)
        │
        └── FACTUAL / COMPARISON
                │
                ▼
        "Retrieving relevant fund facts..."
                │
                ▼
        "Checking source evidence..."
                │
                ▼
        "Generating cited answer..."
                │
                ▼
        AnswerCard rendered
        Source panel updates
        Follow-up chips appear
```

### 10.2 Filter → Query Integration

When user selects a country filter before asking:

- Country filter value is passed as `country` field in `ChatRequest`.
- API uses it as a retrieval metadata filter.
- The answer card shows the active filter: `Filtered to: Canada`

When user selects a fund before asking:

- Fund selection auto-populates example chips relevant to that fund.
- `fund_id` is passed in `ChatRequest`.

### 10.3 Comparison Builder Flow

```
User on Fund Explorer → clicks [+ Compare] on a fund card
        │
        ▼
Fund added to comparison selection (shown in top bar chip)
        │
        ▼
User adds more funds (up to 5)
        │
        ▼
User navigates to Compare Funds screen
        │
        ▼
ComparisonTable populated from API: GET /funds?ids=usa_xlv,usa_vht,canada_hhl
        │
        ▼
User can sort, export, or ask the AI about the comparison set
```

### 10.4 PII Detection State

If user input contains PAN, Aadhaar, account numbers, phone, email, or broker credentials:

```
┌──────────────────────────────────────────────────────────────────┐
│  Please do not share personal or financial account information.  │
│  HealthFundIQ only uses public fund sources and cannot process   │
│  private account or portfolio data.                              │
└──────────────────────────────────────────────────────────────────┘
```

Input is NOT sent to the backend. Detection runs client-side via regex before submission.

PII patterns to detect client-side:
```javascript
/\b[A-Z]{5}[0-9]{4}[A-Z]\b/i        // PAN card format
/\b[0-9]{12}\b/                       // Aadhaar (12 digits)
/\b[0-9]{10,11}\b/                    // Phone number
/[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+/   // Email
```

---

## 11. Guardrail UX

### 11.1 Advice Query (ADVICE intent)

RefusalCard. Warm amber background. Polite, non-alarming, no apology.

```
I can't provide investment advice or buy/sell recommendations.
I can help with factual details such as expense ratio, AUM,
benchmark, holdings, risk rating, investment objective, and
official source documents. What factual question can I answer?
```

**Follow-up chips (always shown after refusal):**
```
[Compare expense ratios]  [Show AUM]
[Show benchmark]           [Show top holdings]
[Show risk rating]         [Country-wise funds]
```

### 11.2 Out-of-Scope Query (OUT_OF_SCOPE intent)

```
HealthFundIQ only covers healthcare, pharma, biotech, med-tech,
and healthcare innovation funds across India, USA, Canada,
China/Hong Kong, Singapore, Japan, and the UK.

Try asking about a fund, country, benchmark, expense ratio,
AUM, holdings, or source document.
```

### 11.3 Language Guardrails (UI level)

Text that must never appear in the UI (even in placeholder or example content):

| Banned phrase | Reason |
|---|---|
| "Recommended fund" | Implies advice |
| "Best fund for you" | Personalized advice |
| "Expected return" | Return prediction |
| "You should invest" | Direct advice |
| "This is safe" | Suitability claim |
| "Buy now" | Transaction advice |
| "Suitable for aggressive investors" | Risk profile advice |
| "Guaranteed" | Performance claim |
| "Low-risk investment" (unless exact source label) | Suitability claim |
| "Top pick" | Editorial ranking |
| "Smart investment" | Subjective recommendation |

---

## 12. Chart Guidelines

### 12.1 Allowed Charts

| Chart | Use | Data source |
|---|---|---|
| Horizontal bar chart | Expense ratio / MER / TER comparison across selected funds | `expense_ratio_or_mer_or_ter` field |
| Horizontal bar chart | AUM / Net Assets comparison | `aum` field |
| Donut chart | Sector exposure (if corpus data exists) | `sector_exposure` field |
| Donut chart | Geographic exposure (if corpus data exists) | `geographic_exposure` field |
| Count bar chart | Funds by country (corpus overview) | Derived from `country` metadata |
| Count bar chart | Funds by subcategory | Derived from `domain_subcategory` |

### 12.2 Charts to Avoid (v1)

Performance charts must not be shown unless historical return data is explicitly ingested and sourced:
- 1Y / 3Y / 5Y return charts.
- NAV trajectory charts.
- Risk-return scatter plots.
- Ranking charts.
- Prediction charts of any kind.

### 12.3 Chart Footer (required on all charts)

```
Source: [source name(s)]
Last updated from sources: [date]
Note: Charts display only corpus-available factual data.
```

### 12.4 Chart Color Rules

Expense ratio chart: use a single neutral color (trust-blue `#2563EB`) for all bars. Do not use green/red to imply cheaper = better.

AUM chart: use `#0D9488` (brand-teal). Do not imply larger AUM = better fund.

Sector/geographic charts: use a multi-color palette from the primary palette without red/green association to any specific sector.

---

## 13. Accessibility Requirements

| Requirement | Standard |
|---|---|
| Text contrast | WCAG AA minimum (4.5:1 for normal text, 3:1 for large) |
| Color independence | Source status must have both color AND text/icon label |
| Keyboard navigation | All filters, source chips, drawers, buttons accessible via keyboard |
| Table headers | All comparison tables have clear `<th>` semantic headers |
| Focus states | All interactive elements have visible focus rings (2px offset) |
| Input labels | All filter and query inputs have associated `<label>` elements |
| Drawer/modal | Accessible via Escape key and focus trap when open |
| Link text | Source links labeled with fund name + URL, not bare "click here" |

---

## 14. Data → UI Field Mapping

### 14.1 `ChatResponse` → UI Components

| API field | UI component | Notes |
|---|---|---|
| `answer` | `AnswerCard` body text | Markdown rendered |
| `source_url` | `SourceCard` primary link | Labeled `[Official]` if matches official_url |
| `platform_url` | `SourceCard` secondary link | Labeled `[Platform]` |
| `last_updated` | `SourceCard` date line | Shows `Last updated from sources:` |
| `fetch_timestamp` | `SourceCard` metadata | Shows `Fetched by HealthFundIQ:` |
| `is_refusal` | `RefusalCard` variant | Replaces AnswerCard |
| `intent` | Debug badge (hidden in prod) | Used for dev/QA |
| `missing_data` | `MissingDataCard` variant | Replaces AnswerCard |
| `chunks_used` | `EvidenceDrawer` content | Listed as chunk IDs with text |
| `fund_name` | `FollowUpChips` — appended to chip queries | E.g. "Show AUM for XLV" instead of "Show AUM" |

### 14.2 `NormalizedFund` → `FundCard` Display Labels

| Normalized field | Display label | Fallback if null |
|---|---|---|
| `fund_name` | Fund name | — |
| `country_or_market` | Country / Market | — |
| `ticker_or_identifier` | Ticker / ISIN | — |
| `fund_type` | Fund Type | — |
| `domain_subcategory` | Subcategory | — |
| `nav_or_price` | NAV / Price | Not found in corpus |
| `aum` | AUM / Net Assets / Fund Size | Not found in corpus |
| `expense_ratio_or_mer_or_ter` | Expense Ratio / MER / TER | Not found in corpus |
| `benchmark` | Benchmark | Not found in corpus |
| `risk_rating_or_riskometer` | Risk Rating / Riskometer | Not found in corpus |
| `fund_house_or_issuer` | Fund House / Issuer | Not found in corpus |
| `fund_management` | Fund Manager | Not found in corpus |
| `investment_objective` | Investment Objective | Not found in corpus |
| `top_10_holdings` | Top 10 Holdings | Not found in corpus |
| `sector_exposure` | Sector Exposure | Not available |
| `geographic_exposure` | Geographic Exposure | Not available |
| `distribution_policy` | Distribution Policy | Not found in corpus |
| `minimum_investment` | Minimum Investment | Not found in corpus |
| `minimum_sip` | Minimum SIP | N/A (ETF) |
| `exit_load_or_redemption_fee` | Exit Load / Redemption Fee | Not found in corpus |
| `official_url` | Official Source | — |
| `platform_url` | Also see (platform) | — |
| `last_updated_from_source` | Last updated from sources | Not available |
| `fetch_timestamp` | Fetched by HealthFundIQ | — |

---

## 15. Streamlit MVP Implementation

### 15.1 Page Configuration

```python
st.set_page_config(
    page_title="HealthFundIQ — Global Healthcare Funds Research",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "HealthFundIQ — Ask. Compare. Verify global healthcare funds — with facts, not financial advice."
    }
)
```

### 15.2 Sidebar

```python
with st.sidebar:
    st.title("HealthFundIQ")
    st.caption("Ask. Compare. Verify.")
    st.divider()

    country = st.selectbox(
        "Country / Market",
        ["All Countries", "India", "USA", "Canada",
         "China/HK", "Japan", "Singapore", "UK/Europe"]
    )
    fund = st.selectbox("Fund", get_fund_options(country))
    subcategory = st.multiselect(
        "Subcategory",
        ["Pharma", "Broad Healthcare", "Biotech",
         "Med-Tech", "Healthcare Innovation"]
    )
    st.divider()
    st.info(
        "**Facts only.** No investment advice.\n\n"
        "Always verify from official fund documents."
    )
```

### 15.3 Main Tab Structure

```python
tab_ask, tab_explorer, tab_compare, tab_sources, tab_about = st.tabs([
    "💬 Ask AI",
    "🔍 Fund Explorer",
    "⚖️ Compare Funds",
    "📋 Sources",
    "ℹ️ About"
])
```

### 15.4 Ask AI Tab — Layout

```python
with tab_ask:
    main_col, source_col = st.columns([0.68, 0.32])

    with main_col:
        # Welcome / example chips on first load
        if not st.session_state.get("chat_started"):
            render_welcome_hero()
            render_example_chips()

        # Chat history
        render_chat_history()

        # Query input
        query = st.chat_input("Ask about expense ratio, AUM, benchmark, holdings...")
        if query:
            handle_query(query, country, fund)

    with source_col:
        render_source_panel()
        render_corpus_health()
```

### 15.5 Component Mapping: Streamlit Primitives

| UI Component | Streamlit Implementation |
|---|---|
| `AnswerCard` | `st.container()` with `st.markdown()` content |
| `FactGrid` | `st.columns(2)` with metric pairs |
| `SourceCard` | `st.expander()` with `st.link_button()` |
| `RefusalCard` | `st.warning()` with amber styling |
| `MissingDataCard` | `st.caption()` inside `st.container()` |
| `DisclaimerBanner` | `st.info()` persistent in sidebar |
| `PromptChips` | `st.button()` row in a `st.columns()` grid |
| `ComparisonTable` | `st.dataframe()` with custom column config |
| `CorpusStatusTable` | `st.dataframe()` with color mapping |
| `EvidenceDrawer` | `st.expander("View extracted text")` |
| `LoadingState` | `st.status()` with sequential step updates |
| `FundCard` | `st.container()` with custom CSS class |
| `CountryBadge` | `st.badge()` (Streamlit 1.34+) or styled `st.caption()` |

### 15.6 Custom CSS (`ui/assets/styles.css`)

```css
/* Card containers */
.fund-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}

.answer-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
}

.refusal-card {
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    border-radius: 12px;
    padding: 16px;
}

.missing-card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
}

/* Source badges */
.badge-official {
    background: #DCFCE7;
    color: #15803D;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 500;
}

.badge-platform {
    background: #F1F5F9;
    color: #475569;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 500;
}

.badge-pdf {
    background: #FEF3C7;
    color: #B45309;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 500;
}

/* Disclaimer banner */
.disclaimer {
    background: #EFF6FF;
    border-left: 3px solid #2563EB;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    color: #1E40AF;
}

/* Fact grid */
.fact-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}

.fact-cell {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 10px 12px;
}

.fact-label {
    font-size: 11px;
    color: #64748B;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 2px;
}

.fact-value {
    font-size: 15px;
    font-weight: 600;
    color: #0F172A;
}

/* Prompt chips */
.prompt-chip {
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 13px;
    cursor: pointer;
}

.prompt-chip:hover {
    background: #E0F2FE;
    border-color: #2563EB;
    color: #1D4ED8;
}

/* Source card */
.source-card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
}

.source-url {
    font-size: 12px;
    color: #2563EB;
    word-break: break-all;
}

.source-meta {
    font-size: 11px;
    color: #64748B;
    margin-top: 4px;
}

/* Missing value text */
.not-found {
    color: #94A3B8;
    font-style: italic;
    font-size: 13px;
}
```

---

## 16. React / Next.js Portfolio Version

### 16.1 Technology Stack

| Layer | Tool |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS |
| Components | shadcn/ui |
| Tables | TanStack Table v8 |
| Charts | Recharts (primary), Apache ECharts (complex) |
| Icons | Lucide React |
| Animation | Motion.dev (v11) |
| API client | TanStack Query (React Query v5) |
| State management | Zustand |
| Forms / input | React Hook Form |

### 16.2 Route Structure

```
app/
├── page.tsx                  # Home / Welcome screen
├── research/
│   └── page.tsx              # Ask AI screen
├── funds/
│   ├── page.tsx              # Fund Explorer
│   └── [fundId]/
│       └── page.tsx          # Fund Detail
├── compare/
│   └── page.tsx              # Compare Funds
├── sources/
│   └── page.tsx              # Sources & Evidence
└── about/
    └── page.tsx              # About / Methodology
```

### 16.3 Component Directory

```
components/
├── layout/
│   ├── AppShell.tsx          # Three-panel layout wrapper
│   ├── TopBar.tsx            # Wordmark, tagline, refresh, disclaimer
│   ├── Sidebar.tsx           # Filters + navigation
│   └── SourcePanel.tsx       # Right-side source panel
├── chat/
│   ├── QueryInput.tsx        # Full-width input
│   ├── PromptChips.tsx       # Example question chips
│   ├── AnswerCard.tsx        # Main answer container (4 variants)
│   ├── FactGrid.tsx          # Field-value grid
│   ├── FactChip.tsx          # Single field chip with source
│   ├── RefusalCard.tsx       # Advice refusal state
│   ├── MissingDataCard.tsx   # Missing corpus data state
│   ├── LoadingState.tsx      # Sequential loading steps
│   └── FollowUpChips.tsx     # Factual follow-up suggestions
├── funds/
│   ├── FundCard.tsx          # Browseable fund summary
│   ├── FundHeader.tsx        # Fund name + identity strip
│   ├── FundFactsGrid.tsx     # Full fund fact grid on detail page
│   ├── HoldingsTable.tsx     # Top 10 holdings table
│   └── ExposureChart.tsx     # Sector/geographic donut
├── compare/
│   ├── ComparisonTable.tsx   # TanStack Table comparison grid
│   ├── ComparisonToolbar.tsx # Fund selector + sort + export
│   └── ComparisonExport.tsx  # CSV export logic
├── sources/
│   ├── SourceCard.tsx        # Source URL + badge + metadata
│   ├── EvidenceDrawer.tsx    # Expandable extracted chunk
│   ├── SourceBadge.tsx       # [Official]/[Platform]/[PDF] pill
│   └── CorpusStatusTable.tsx # Per-fund ingestion status
└── common/
    ├── DisclaimerBanner.tsx  # Persistent facts-only strip
    ├── CountryBadge.tsx      # Country label pill
    ├── EmptyState.tsx        # No fund / no query state
    ├── MetricChip.tsx        # Value display with label
    └── NotFound.tsx          # Not found in corpus display
```

### 16.4 Animation Guidelines (Motion.dev)

| Interaction | Animation | Duration |
|---|---|---|
| Answer card appears | `fadeIn` + `y: 8 → 0` | 200ms ease-out |
| Source panel opens | `slideInFromRight` | 250ms ease-out |
| Evidence drawer expands | Height expand with `AnimatePresence` | 200ms ease |
| Fund card hover | Border color transition + subtle shadow lift | 150ms |
| Loading state step | Fade between steps | 150ms |
| Comparison table row | Fade in on add | 150ms |
| Filter change (table) | Skeleton loading overlay | 200ms |
| Navigation transition | `fadeIn` | 150ms |

**Avoid:**
- Bounce animations.
- Long duration transitions (>350ms).
- Glowing or pulsing effects.
- Number counter roll-ups on financial values (can imply live market data).
- "Winning" confetti or highlight animations.

---

## 17. Trust and Compliance Rules (Non-Negotiable)

### 17.1 Always Display

- Facts-only disclaimer — on every screen, every time.
- Source link — on every factual answer, without exception.
- Last updated from source — wherever available.
- Fetch timestamp — so users know how old the data is.
- Missing-data state — never fake a value that isn't in the corpus.

### 17.2 Never Display

- Any form of investment recommendation.
- Return prediction or performance forecast.
- "Best fund" label unless explicitly based on a corpus factual field (e.g., lowest expense ratio) and stated neutrally.
- Red/green coloring to imply fund quality.
- Suitability labels (aggressive, conservative, good for long-term, etc.).
- Any PII collected, stored, or echoed back.

### 17.3 Acceptable vs Unacceptable Language

| Situation | Use | Avoid |
|---|---|---|
| Expense ratio comparison | "Among selected funds, XLV has the lowest available expense ratio (0.09%) in the current corpus." | "XLV is the best value fund." |
| AUM display | "XLV AUM: USD 42.1B (source: SSGA)" | "XLV is the largest and most popular fund." |
| Risk display | "Risk rating: Very High (source: Groww, retrieved from riskometer label)" | "This fund is risky. Do not invest." |
| Missing field | "Not found in corpus for this fund." | (blank field) or "0" or "N/A" |
| Source display | "Source: ssga.com (Official) · Last updated: 2026-06-01" | No source link shown |

---

## 18. Edge and Error States

| State | Display |
|---|---|
| Empty chat (no query yet) | Welcome hero + example chips |
| No matching fund for filter | "No funds match the selected filters. Try changing the country or subcategory." |
| Source fetch failed | Corpus status shows `✗ Failed`. Answer may still come from stale cached chunks. Show: "Source fetch failed during the latest refresh. Data shown may be from a previous ingestion run." |
| All sources for a fund failed | "No current data is available for this fund. The last successful fetch was [date]. Please check the official source directly." |
| Comparison with missing values | Cells show `Not found` in muted gray. Footer note: "Some funds do not publish this field in the current source set." |
| PDF parse failure | Corpus status shows `⚠ PDF parse error`. HTML chunks still used. No visible error to user unless all sources failed. |
| API unavailable | Full-screen error: "HealthFundIQ is temporarily unavailable. Please try again shortly." With retry button. |

---

## 19. MVP Build Order (Streamlit)

### Phase 1 — Functional Core

1. `AppShell`: sidebar + main area + source panel skeleton.
2. `DisclaimerBanner`: persistent in sidebar.
3. `QueryInput`: `st.chat_input` wired to `/chat` API.
4. `AnswerCard` — factual variant: renders `answer`, `source_url`, `last_updated`.
5. `SourceCard`: shows source URL, badge, timestamp.
6. `RefusalCard`: amber `st.warning` for `is_refusal = true`.
7. `MissingDataCard`: gray `st.info` for `missing_data = true`.
8. `SidebarFilters`: country + fund `st.selectbox`.

### Phase 2 — Research Workspace

1. `PromptChips`: example question buttons.
2. `FactGrid`: structured key-facts display.
3. `FollowUpChips`: suggested factual follow-ups.
4. `LoadingState`: `st.status` sequential steps.
5. `FundCard`: browseable fund grid (Fund Explorer tab).
6. `ComparisonTable`: `st.dataframe` side-by-side (Compare Funds tab).
7. `CorpusStatusTable`: ingestion run status (Sources tab).
8. `EvidenceDrawer`: `st.expander` extracted chunk viewer.

### Phase 3 — Visual Polish

1. Apply `styles.css` for card containers, badges, chips.
2. Source panel column (right-side, 32% width).
3. Export CSV from comparison table.
4. About / Methodology tab with full disclaimer.
5. Country group headers in Fund Explorer.
6. Mobile stacked layout adjustments.

### Phase 4 — React Portfolio Version

1. Next.js app shell with three-panel layout.
2. TanStack Table comparison grid.
3. Motion.dev answer card animation.
4. Recharts sector exposure donut.
5. Fund Detail route with full evidence panel.
6. shadcn/ui component polish.

---

## 20. Final Design Summary

HealthFundIQ is built on four compounding design commitments:

**Evidence-first:** Every number, every field, every comparison traces back to a named public source URL, a source type label, and a fetch timestamp. Users can verify anything.

**Restraint-by-design:** Colors, copy, layout, and interaction never imply advice, prediction, or recommendation. The product makes its scope visible and enforces it politely.

**Normalized clarity:** 7 markets, 7 terminologies, one vocabulary. Expense ratio, MER, and TER all appear as "Expense Ratio / MER / TER." The user does not need to know the local term.

**Trust at every layer:** The top bar shows the last corpus refresh. The source panel shows official vs platform vs PDF. The corpus status page shows which sources succeeded or failed. Nothing is hidden.

> **HealthFundIQ** — Ask. Compare. Verify global healthcare funds — with facts, not financial advice.
