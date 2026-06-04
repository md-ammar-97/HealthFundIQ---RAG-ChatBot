"""
One-time backfill: parse all HTML/PDF files in data/raw/ and write clean
JSON files to data/parsed/ without re-fetching from the internet.

Usage:
    python -m ingestion.backfill_parsed

Safe to re-run — overwrites existing JSON files with fresh data.
Does NOT touch ChromaDB.
"""
import io
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta
from ingestion.html_parser import parse_html
from ingestion.pdf_parser import parse_pdf
from ingestion.normalizer import normalize, merge_normalized, NormalizedFund
from ingestion.parsed_store import save_parsed
from ingestion.logger import get_logger

logger = get_logger("ingestion.backfill_parsed")
IST = timezone(timedelta(hours=5, minutes=30))

RAW_DIR = Path("data/raw")


def _load_sources() -> dict[str, dict]:
    with open("config/sources.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {s["id"]: s for s in data["funds"]}


def _country_slug(country: str) -> str:
    return country.lower().replace("/", "_").replace(" ", "_")


def backfill_fund(fund_id: str, source: dict) -> bool:
    country = source["country"]
    fund_name = source["fund_name"]
    ticker = source.get("ticker")
    isin = source.get("isin")
    ts = datetime.now(IST).isoformat()

    raw_dir = RAW_DIR / _country_slug(country) / fund_id
    if not raw_dir.exists():
        logger.warning(f"{fund_id}: no raw directory found at {raw_dir} — skipping")
        return False

    normalized_objects: list[NormalizedFund] = []

    # -- Platform HTML --
    platform_html = raw_dir / "platform_page.html"
    if platform_html.exists():
        html = platform_html.read_text(encoding="utf-8", errors="replace")
        parsed = parse_html(
            fund_id=fund_id, country=country, fund_name=fund_name,
            ticker=ticker, isin=isin,
            source_url=source["platform_url"],
            source_type="platform",
            fetch_timestamp=ts,
            html=html,
        )
        if parsed.parse_success:
            normalized_objects.append(normalize(parsed, source))
            logger.info(f"{fund_id}: parsed platform HTML ({len(html)} chars)")
        else:
            logger.warning(f"{fund_id}: platform HTML parse_success=False")

    # -- Official HTML --
    official_html = raw_dir / "official_page.html"
    if official_html.exists():
        html = official_html.read_text(encoding="utf-8", errors="replace")
        parsed_off = parse_html(
            fund_id=fund_id, country=country, fund_name=fund_name,
            ticker=ticker, isin=isin,
            source_url=source.get("official_url", ""),
            source_type="official",
            fetch_timestamp=ts,
            html=html,
        )
        if parsed_off.parse_success:
            normalized_objects.append(normalize(parsed_off, source))
            logger.info(f"{fund_id}: parsed official HTML ({len(html)} chars)")
        else:
            logger.warning(f"{fund_id}: official HTML parse_success=False")

    # -- PDF Factsheet --
    pdf_file = raw_dir / "factsheet_page.pdf"
    if pdf_file.exists():
        pdf_bytes = pdf_file.read_bytes()
        parsed_pdf = parse_pdf(
            fund_id=fund_id, country=country, fund_name=fund_name,
            ticker=ticker, isin=isin,
            source_url=source.get("pdf_url", ""),
            fetch_timestamp=ts,
            pdf_bytes=pdf_bytes,
        )
        if parsed_pdf.parse_success:
            normalized_objects.append(normalize(parsed_pdf, source))
            logger.info(f"{fund_id}: parsed PDF factsheet ({len(pdf_bytes)} bytes)")
        else:
            logger.warning(f"{fund_id}: PDF parse_success=False")

    if not normalized_objects:
        logger.error(f"{fund_id}: no successful parse from any cached file — skipping")
        return False

    # -- Merge (official > pdf > platform) --
    official_norm = next((n for n in normalized_objects if n.source_type == "official"), None)
    platform_norm = next((n for n in normalized_objects if n.source_type == "platform"), None)
    pdf_norm      = next((n for n in normalized_objects if n.source_type == "pdf"), None)

    merged = merge_normalized(official_norm, pdf_norm)
    merged = merge_normalized(merged, platform_norm)

    # -- Save JSON --
    path = save_parsed(merged)
    logger.info(f"{fund_id}: JSON written to {path} | missing={merged.missing_fields}")
    return True


def backfill_all() -> None:
    sources = _load_sources()

    # Discover fund IDs from existing raw directories
    raw_fund_dirs = [
        d for d in RAW_DIR.rglob("*")
        if d.is_dir() and not d.parent == RAW_DIR  # skip country-level dirs
        and any(d.iterdir())  # non-empty
    ]

    fund_ids_in_raw = {d.name for d in raw_fund_dirs}
    logger.info(f"Found {len(fund_ids_in_raw)} fund directories in data/raw/")

    ok, skip = 0, 0
    for fund_id in sorted(fund_ids_in_raw):
        source = sources.get(fund_id)
        if not source:
            logger.warning(f"{fund_id}: not found in sources.yaml — skipping")
            skip += 1
            continue
        success = backfill_fund(fund_id, source)
        if success:
            ok += 1
        else:
            skip += 1

    logger.info(f"Backfill complete | written={ok} skipped={skip}")


if __name__ == "__main__":
    backfill_all()
