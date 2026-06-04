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
