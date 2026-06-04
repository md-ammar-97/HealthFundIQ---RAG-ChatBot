import pytest
from ingestion.normalizer import NormalizedFund
from ingestion.chunker import chunk_fund


FUND_NAME = "HDFC Pharma and Healthcare Direct Growth Fund"  # long enough for MIN_CHUNK_CHARS


def _make_fund(**kwargs) -> NormalizedFund:
    defaults = dict(
        fund_id="test_xlv", country_or_market="USA",
        fund_name=FUND_NAME, ticker_or_identifier="TEST",
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
    assert FUND_NAME in cost_chunk.text
    assert "USA" in cost_chunk.text


def test_chunk_metadata_no_none():
    fund = _make_fund()
    chunks = chunk_fund(fund)
    for chunk in chunks:
        assert chunk.ticker is not None  # "" not None
        assert chunk.isin is not None
        assert chunk.official_url is not None


def test_long_objective_splits():
    # MAX_CHUNK_TOKENS * CHARS_PER_TOKEN = 512 * 4 = 2048; objective prefix adds ~65 chars
    # Use 1100 "A " repetitions = 2200 chars, total content > 2048 → forces split
    long_obj = "A " * 1100
    fund = _make_fund(investment_objective=long_obj)
    chunks = chunk_fund(fund)
    obj_chunks = [c for c in chunks if "investment_objective" in c.chunk_id]
    assert len(obj_chunks) > 1
