import io
import pdfplumber
from ingestion.html_parser import ParsedFund, _clean
from ingestion.logger import get_logger

logger = get_logger("ingestion.pdf_parser")
MAX_FIELD_CHARS = 2000


def parse_pdf(
    fund_id: str,
    country: str,
    fund_name: str,
    ticker: str | None,
    isin: str | None,
    source_url: str,
    fetch_timestamp: str,
    pdf_bytes: bytes,
) -> ParsedFund:
    raw_fields: dict[str, str] = {}
    notes: list[str] = []

    try:
        fp = io.BytesIO(pdf_bytes) if isinstance(pdf_bytes, bytes) else open(pdf_bytes, "rb")
        with pdfplumber.open(fp) as pdf:
            all_text_blocks: list[str] = []
            all_tables: list[list[list]] = []

            for page in pdf.pages:
                text = page.extract_text() or ""
                if text.strip():
                    all_text_blocks.append(text)
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)

            full_text = "\n".join(all_text_blocks)

            if not full_text.strip():
                notes.append("PDF appears to be image-only (no selectable text)")
                logger.warning(f"{fund_id}: PDF has no selectable text — image scan?")
                return ParsedFund(
                    fund_id=fund_id, country=country, fund_name=fund_name,
                    ticker=ticker, isin=isin, source_url=source_url,
                    source_type="pdf", fetch_timestamp=fetch_timestamp,
                    parse_method="pdfplumber", parse_success=False,
                    raw_fields={}, extraction_notes=notes,
                )

            # Extract from text blocks using line-by-line parsing
            raw_fields = _extract_from_text(full_text, fund_name)

            # Extract from tables
            for table in all_tables:
                _extract_from_table(table, raw_fields)

    except Exception as e:
        if "password" in str(e).lower() or "encrypted" in str(e).lower():
            notes.append("PDF is password-protected — cannot extract")
            logger.warning(f"{fund_id}: PDF is password-protected")
        else:
            notes.append(f"PDF parse error: {e}")
            logger.error(f"{fund_id}: PDF parse exception: {e}")
        return ParsedFund(
            fund_id=fund_id, country=country, fund_name=fund_name,
            ticker=ticker, isin=isin, source_url=source_url,
            source_type="pdf", fetch_timestamp=fetch_timestamp,
            parse_method="pdfplumber", parse_success=False,
            raw_fields={}, extraction_notes=notes,
        )

    success = len(raw_fields) >= 2
    logger.info(f"{fund_id}: PDF extracted {len(raw_fields)} fields, success={success}")

    return ParsedFund(
        fund_id=fund_id, country=country, fund_name=fund_name,
        ticker=ticker, isin=isin, source_url=source_url,
        source_type="pdf", fetch_timestamp=fetch_timestamp,
        parse_method="pdfplumber", parse_success=success,
        raw_fields=raw_fields, extraction_notes=notes,
    )


def _extract_from_text(text: str, fund_name: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    import re

    patterns = {
        "Expense Ratio": r"(?:expense ratio|ter|ongoing charges?)[:\s]+([0-9]+\.?[0-9]*\s*%)",
        "AUM": r"(?:fund size|net assets|aum|total assets)[:\s]+([\$\£\€\¥]?[\s]?[0-9,\.]+\s*(?:bn|mn|m|b|billion|million)?)",
        "NAV": r"(?:nav|net asset value)[:\s]+([\$\£\€\¥\₩]?[\s]?[0-9,\.]+)",
        "Benchmark": r"(?:benchmark|reference index|tracks?)[:\s]+([A-Za-z0-9 &\-\.®™]+(?:Index)?)",
        "Risk Rating": r"(?:risk rating|srri|risk indicator)[:\s]+([A-Za-z0-9 \/]+)",
        "Fund Manager": r"(?:portfolio manager|investment manager|managed by)[:\s]+([A-Za-z ,\.]+)",
        "Investment Objective": r"(?:investment objective|fund objective|objective)[:\s\n]+([A-Za-z][^\n]{30,300})",
        "Distribution Policy": r"(?:distribution policy|dividend)[:\s]+([A-Za-z]+(?:ulating|ributing)?)",
    }

    for label, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = _clean(m.group(1))
            if val:
                fields[label] = val[:MAX_FIELD_CHARS]

    return fields


def _extract_from_table(table: list[list], fields: dict[str, str]) -> None:
    if not table:
        return
    for row in table:
        if not row or len(row) < 2:
            continue
        label = _clean(str(row[0] or ""))
        value = _clean(str(row[1] or ""))
        if label and value and label not in fields:
            fields[label] = value[:MAX_FIELD_CHARS]
