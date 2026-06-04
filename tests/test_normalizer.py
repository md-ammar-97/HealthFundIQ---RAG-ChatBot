from ingestion.html_parser import ParsedFund
from ingestion.normalizer import normalize

SOURCE_META = {
    "id": "usa_xlv", "country": "USA", "fund_name": "XLV",
    "ticker": "XLV", "isin": None, "fund_type": "ETF",
    "domain_subcategory": "Broad Healthcare", "currency": "USD",
    "exchange": "NYSE Arca", "platform_url": "https://etf.com/XLV",
    "official_url": "https://ssga.com/xlv",
}


def _make_parsed(**raw_fields) -> ParsedFund:
    return ParsedFund(
        fund_id="usa_xlv", country="USA", fund_name="XLV",
        ticker="XLV", isin=None,
        source_url="https://ssga.com/xlv", source_type="official",
        fetch_timestamp="2026-06-02T10:00:00+05:30",
        parse_method="beautifulsoup", parse_success=True,
        raw_fields=raw_fields,
    )


def test_expense_ratio_mapped():
    p = _make_parsed(**{"Expense Ratio": "0.09%"})
    n = normalize(p, SOURCE_META)
    assert n.expense_ratio_or_mer_or_ter == "0.09%"


def test_canada_mer_mapped():
    meta = {**SOURCE_META, "country": "Canada", "id": "canada_hhl"}
    p = ParsedFund(
        fund_id="canada_hhl", country="Canada", fund_name="HHL",
        ticker="HHL", isin=None,
        source_url="https://harvestportfolios.com/etf/hhl/",
        source_type="official",
        fetch_timestamp="2026-06-02T10:00:00+05:30",
        parse_method="beautifulsoup", parse_success=True,
        raw_fields={"MER": "0.85%", "Risk Rating": "Medium"},
    )
    n = normalize(p, meta)
    assert n.expense_ratio_or_mer_or_ter == "0.85%"
    assert n.risk_rating_or_riskometer == "Medium"


def test_missing_field_in_missing_list():
    p = _make_parsed()  # no raw fields
    n = normalize(p, SOURCE_META)
    assert "expense_ratio_or_mer_or_ter" in n.missing_fields
