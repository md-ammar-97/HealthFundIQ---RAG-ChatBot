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
    fund_name: str | None = None


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


class FundDetails(BaseModel):
    fund_id: str
    country_or_market: str
    fund_name: str
    ticker_or_identifier: str | None = None
    fund_type: str
    domain_subcategory: str
    currency: str
    exchange: str | None = None
    source_type: str | None = None
    platform_url: str
    official_url: str | None = None
    last_updated_from_source: str | None = None
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
    missing_fields: list[str] = []
    extraction_notes: list[str] = []


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    corpus_chunks: int
