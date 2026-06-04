"""
CLI entry point: python -m ingestion.run_ingestion
Runs the full ingestion pipeline for all non-backup funds in sources.yaml.

Pipeline per fund:
  fetch → data/raw/  →  parse+normalize+merge  →  data/parsed/{fund_id}.json
  → load from JSON → chunk → embed → ChromaDB
"""
import json
import os
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta
from ingestion.crawler import fetch
from ingestion.html_parser import parse_html
from ingestion.pdf_parser import parse_pdf
from ingestion.normalizer import normalize, merge_normalized, NormalizedFund
from ingestion.parsed_store import save_parsed, load_parsed
from ingestion.chunker import chunk_fund
from embeddings.embedder import encode_chunks
from embeddings.store import upsert_chunks
from ingestion.logger import get_logger

logger = get_logger("ingestion.run_ingestion")
IST = timezone(timedelta(hours=5, minutes=30))


def _load_sources() -> list[dict]:
    with open("config/sources.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [s for s in data["funds"] if not s.get("is_backup", False)]


def _save_raw(fund_id: str, country: str, source_type: str, content: str | bytes, ext: str) -> None:
    country_slug = country.lower().replace("/", "_").replace(" ", "_")
    path = Path(f"data/raw/{country_slug}/{fund_id}")
    path.mkdir(parents=True, exist_ok=True)
    filename = f"{source_type}_page.{ext}"
    mode = "wb" if isinstance(content, bytes) else "w"
    encoding = None if isinstance(content, bytes) else "utf-8"
    with open(path / filename, mode, encoding=encoding) as f:
        f.write(content)


def _log_result(log: dict) -> None:
    os.makedirs("logs", exist_ok=True)
    with open("logs/ingestion.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")


def ingest_fund(source: dict, run_id: str) -> dict:
    fund_id = source["id"]
    country = source["country"]
    fund_name = source["fund_name"]
    ticker = source.get("ticker")
    isin = source.get("isin")

    log = {
        "run_id": run_id,
        "fund_id": fund_id,
        "country": country,
        "chunks_upserted": 0,
        "chunks_skipped": 0,
        "error_message": None,
    }

    normalized_objects: list[NormalizedFund] = []

    # -- Fetch platform URL --
    platform_raw = fetch(
        fund_id=fund_id,
        url=source["platform_url"],
        source_type="platform",
        use_playwright=source.get("use_playwright", False),
    )
    if platform_raw.fetch_success:
        _save_raw(fund_id, country, "platform", platform_raw.raw_content, "html")
        parsed = parse_html(
            fund_id=fund_id, country=country, fund_name=fund_name,
            ticker=ticker, isin=isin,
            source_url=source["platform_url"],
            source_type="platform",
            fetch_timestamp=platform_raw.fetch_timestamp,
            html=platform_raw.raw_content,
        )
        if parsed.parse_success:
            norm = normalize(parsed, source)
            normalized_objects.append(norm)
    else:
        logger.warning(f"{fund_id}: platform fetch failed — {platform_raw.error_message}")

    # -- Fetch official URL (if present) --
    if source.get("official_url"):
        official_raw = fetch(
            fund_id=fund_id,
            url=source["official_url"],
            source_type="official",
            use_playwright=source.get("official_use_playwright", False),
        )
        if official_raw.fetch_success:
            _save_raw(fund_id, country, "official", official_raw.raw_content, "html")
            parsed_off = parse_html(
                fund_id=fund_id, country=country, fund_name=fund_name,
                ticker=ticker, isin=isin,
                source_url=source["official_url"],
                source_type="official",
                fetch_timestamp=official_raw.fetch_timestamp,
                html=official_raw.raw_content,
            )
            if parsed_off.parse_success:
                norm_off = normalize(parsed_off, source)
                normalized_objects.append(norm_off)

    # -- Fetch PDF (if present) --
    if source.get("has_pdf") and source.get("pdf_url"):
        pdf_raw = fetch(
            fund_id=fund_id,
            url=source["pdf_url"],
            source_type="pdf",
        )
        if pdf_raw.fetch_success:
            _save_raw(fund_id, country, "factsheet", pdf_raw.raw_content, "pdf")
            parsed_pdf = parse_pdf(
                fund_id=fund_id, country=country, fund_name=fund_name,
                ticker=ticker, isin=isin,
                source_url=source["pdf_url"],
                fetch_timestamp=pdf_raw.fetch_timestamp,
                pdf_bytes=pdf_raw.raw_content,
            )
            if parsed_pdf.parse_success:
                norm_pdf = normalize(parsed_pdf, source)
                normalized_objects.append(norm_pdf)

    if not normalized_objects:
        log["error_message"] = "No successful parse from any source"
        logger.error(f"{fund_id}: no successful parse — skipping upsert")
        _log_result(log)
        return log

    # -- Merge all normalized objects (official > pdf > platform) --
    official_norm = next((n for n in normalized_objects if n.source_type == "official"), None)
    platform_norm = next((n for n in normalized_objects if n.source_type == "platform"), None)
    pdf_norm = next((n for n in normalized_objects if n.source_type == "pdf"), None)

    merged = merge_normalized(official_norm, pdf_norm)
    merged = merge_normalized(merged, platform_norm)

    # -- Try backup URLs if important fields are still missing --
    _IMPORTANT_FIELDS = {
        "expense_ratio_or_mer_or_ter", "aum", "benchmark",
        "fund_management", "fund_house_or_issuer",
        "risk_rating_or_riskometer", "investment_objective",
    }
    backup_urls = source.get("backup_platform_urls") or []
    for i, backup_url in enumerate(backup_urls):
        still_missing = set(merged.missing_fields or []) & _IMPORTANT_FIELDS
        if not still_missing:
            break
        logger.info(f"{fund_id}: still missing {still_missing} — trying backup {backup_url}")
        backup_raw = fetch(
            fund_id=fund_id,
            url=backup_url,
            source_type="platform",
            use_playwright=False,
        )
        if not backup_raw.fetch_success:
            logger.warning(f"{fund_id}: backup fetch failed — {backup_raw.error_message}")
            continue
        _save_raw(fund_id, country, f"backup_{i}", backup_raw.raw_content, "html")
        parsed_backup = parse_html(
            fund_id=fund_id, country=country, fund_name=fund_name,
            ticker=ticker, isin=isin,
            source_url=backup_url,
            source_type="platform",
            fetch_timestamp=backup_raw.fetch_timestamp,
            html=backup_raw.raw_content,
        )
        if parsed_backup.parse_success:
            norm_backup = normalize(parsed_backup, source)
            merged = merge_normalized(merged, norm_backup)
            logger.info(f"{fund_id}: filled from backup[{i}] — missing now: {merged.missing_fields}")

    # -- Save clean JSON (authoritative data source for chunker) --
    save_parsed(merged)

    # -- Reload from JSON to ensure chunker reads clean persisted data --
    fund_data = load_parsed(fund_id, country)
    if fund_data is None:
        log["error_message"] = "JSON save/load round-trip failed"
        logger.error(f"{fund_id}: could not reload parsed JSON")
        _log_result(log)
        return log

    # -- Chunk --
    chunks = chunk_fund(fund_data)

    if not chunks:
        log["error_message"] = "No chunks produced"
        _log_result(log)
        return log

    # -- Embed and upsert --
    encoded = encode_chunks(chunks)
    upserted, skipped = upsert_chunks(encoded)

    log["chunks_upserted"] = upserted
    log["chunks_skipped"] = skipped
    log["fields_extracted"] = [f for f in [
        "nav_or_price", "aum", "expense_ratio_or_mer_or_ter",
        "minimum_investment", "minimum_sip", "exit_load_or_redemption_fee",
        "benchmark", "fund_management", "fund_house_or_issuer",
        "investment_objective", "risk_rating_or_riskometer", "top_10_holdings",
        "sector_exposure", "geographic_exposure", "distribution_policy",
    ] if getattr(fund_data, f)]
    log["fields_missing"] = fund_data.missing_fields
    _log_result(log)
    logger.info(f"{fund_id}: done | upserted={upserted} skipped={skipped}")
    return log


def ingest_all() -> None:
    sources = _load_sources()
    run_id = datetime.now(IST).isoformat()
    logger.info(f"Starting ingestion run {run_id} for {len(sources)} funds")

    results = []
    for source in sources:
        try:
            result = ingest_fund(source, run_id)
            results.append(result)
        except Exception as e:
            logger.error(f"{source['id']}: unexpected error: {e}", exc_info=True)

    success = sum(1 for r in results if r.get("chunks_upserted", 0) > 0)
    failed = len(results) - success
    logger.info(f"Ingestion complete | success={success} failed={failed}")


if __name__ == "__main__":
    ingest_all()
