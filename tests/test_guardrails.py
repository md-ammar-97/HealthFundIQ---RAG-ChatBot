import pytest
from guardrails.classifier import classify, contains_pii

ADVICE_QUERIES = [
    "Should I buy XLV?",
    "Which healthcare fund is best for me?",
    "Will XLV give better returns than VHT?",
    "Can you build a healthcare portfolio for me?",
    "Is this a good time to buy healthcare ETFs?",
    "How much money should I invest in IBB?",
]

FACTUAL_QUERIES = [
    "What is the expense ratio of HDFC Pharma and Healthcare Fund?",
    "What benchmark does XLV track?",
    "Who manages Nippon India Pharma Fund?",
    "What are the top holdings of IBB?",
    "Which funds are biotech-focused?",
]

# Holdings must NOT trigger ADVICE (contains "hold")
FALSE_POSITIVE_RISKS = [
    "What are the top holdings of XLV?",
    "Show me the holdings of VHT",
]

PII_QUERIES = [
    "ABCDE1234F",          # PAN
    "123456789012",        # Aadhaar
    "user@example.com",    # Email
]


def test_advice_queries_refused():
    for q in ADVICE_QUERIES:
        assert classify(q) == "ADVICE", f"Expected ADVICE for: {q!r}"


def test_factual_queries_not_refused():
    for q in FACTUAL_QUERIES:
        intent = classify(q)
        assert intent in ("FACTUAL", "COMPARISON"), f"Expected FACTUAL/COMPARISON for: {q!r}, got {intent}"


def test_holdings_not_false_positive():
    for q in FALSE_POSITIVE_RISKS:
        intent = classify(q)
        assert intent != "ADVICE", f"False positive ADVICE for holdings query: {q!r}"


def test_pii_detection():
    for q in PII_QUERIES:
        assert contains_pii(q), f"PII not detected in: {q!r}"
