// API types — mirrors backend Pydantic models exactly

export interface ChatRequest {
  query: string;
  country?: string | null;
  fund_id?: string | null;
}

export interface ChatResponse {
  answer: string;
  source_url: string | null;
  platform_url: string | null;
  last_updated: string | null;
  fetch_timestamp: string | null;
  is_refusal: boolean;
  intent: string;
  missing_data: boolean;
  fund_name: string | null;
}

export interface FundListItem {
  fund_id: string;
  country: string;
  fund_name: string;
  ticker: string | null;
  isin: string | null;
  fund_type: string;
  domain_subcategory: string;
  currency: string;
  exchange: string | null;
  platform_url: string;
  official_url: string | null;
  is_backup: boolean;
}

export interface Holding {
  name: string;
  weight: string | number;
  ticker?: string;
  isin?: string;
}

export interface ExposureItem {
  label: string;
  weight: string | number;
}

export interface FundDetails {
  fund_id: string;
  country_or_market: string;
  fund_name: string;
  ticker_or_identifier: string | null;
  fund_type: string;
  domain_subcategory: string;
  currency: string;
  exchange: string | null;
  source_type: string | null;
  platform_url: string;
  official_url: string | null;
  last_updated_from_source: string | null;
  fetch_timestamp: string;
  nav_or_price: string | null;
  aum: string | null;
  expense_ratio_or_mer_or_ter: string | null;
  minimum_investment: string | null;
  minimum_sip: string | null;
  exit_load_or_redemption_fee: string | null;
  benchmark: string | null;
  fund_management: string | null;
  fund_house_or_issuer: string | null;
  investment_objective: string | null;
  risk_rating_or_riskometer: string | null;
  distribution_policy: string | null;
  tax_information: string | null;
  top_10_holdings: Holding[] | null;
  sector_exposure: ExposureItem[] | null;
  geographic_exposure: ExposureItem[] | null;
  documents: string[] | null;
  missing_fields: string[];
  extraction_notes: string[];
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  corpus_chunks: number;
}

// UI-only types
export type SourceType = "official" | "platform" | "pdf";

export interface SourceCardData {
  url: string;
  sourceType: SourceType;
  fundName?: string;
  lastUpdated?: string | null;
  fetchTimestamp?: string | null;
  answerExcerpt?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
  timestamp: Date;
}

export type Intent = "FACTUAL" | "COMPARISON" | "FUND_LIST" | "AGGREGATION" | "ADVICE" | "OUT_OF_SCOPE" | "PII_DETECTED";

export const COUNTRIES = [
  "India", "USA", "Canada", "China/HK", "Japan", "Singapore", "UK/Europe",
] as const;

export type Country = typeof COUNTRIES[number];
