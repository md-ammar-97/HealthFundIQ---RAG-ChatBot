import time
import requests
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Literal
from ingestion.logger import get_logger

logger = get_logger("ingestion.crawler")

IST = timezone(timedelta(hours=5, minutes=30))
MIN_HTML_CHARS = 500
MIN_PDF_BYTES = 1000
MAX_PDF_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class RawFetch:
    fund_id: str
    url: str
    source_type: Literal["platform", "official", "pdf"]
    content_type: Literal["html", "pdf"]
    raw_content: str | bytes
    fetch_timestamp: str
    http_status: int
    fetch_method: Literal["requests", "playwright"]
    content_length: int
    fetch_success: bool
    error_message: str | None


def _now_ist() -> str:
    return datetime.now(IST).isoformat()


def _fetch_static(url: str, is_pdf: bool = False) -> tuple[int, str | bytes | None, str | None]:
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(
                url,
                headers=HEADERS,
                timeout=30,
                allow_redirects=True,
                stream=is_pdf,
            )
            if is_pdf:
                if resp.status_code == 200:
                    content = resp.content
                    if len(content) > MAX_PDF_BYTES:
                        return resp.status_code, None, f"PDF too large: {len(content)} bytes"
                    return resp.status_code, content, None
            else:
                return resp.status_code, resp.text, None
        except requests.exceptions.Timeout:
            err = "Timeout"
        except requests.exceptions.SSLError as e:
            return 0, None, f"SSL error: {e}"
        except requests.exceptions.ConnectionError as e:
            err = f"Connection error: {e}"
        except Exception as e:
            err = str(e)

        if attempt < MAX_RETRIES - 1:
            time.sleep(BACKOFF_BASE ** attempt)

    return 0, None, err


def _fetch_playwright(url: str) -> tuple[int, str | None, str | None]:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        return 0, None, "Playwright not installed. Run: playwright install chromium"

    for attempt in range(MAX_RETRIES):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent=HEADERS["User-Agent"],
                    locale="en-US",
                )
                page = ctx.new_page()
                page.goto(url, wait_until="networkidle", timeout=45000)
                # Accept cookie banners if present
                for selector in [
                    "button:has-text('Accept All')",
                    "button:has-text('Accept Cookies')",
                    "button:has-text('I Accept')",
                    "[id*='accept']",
                ]:
                    try:
                        btn = page.locator(selector).first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            page.wait_for_timeout(1000)
                            break
                    except Exception:
                        pass
                page.wait_for_timeout(3000)
                html = page.content()
                browser.close()
                return 200, html, None
        except PWTimeout:
            err = "Playwright timeout"
        except Exception as e:
            err = str(e)

        if attempt < MAX_RETRIES - 1:
            time.sleep(BACKOFF_BASE ** attempt)

    return 0, None, err


def fetch(
    fund_id: str,
    url: str,
    source_type: Literal["platform", "official", "pdf"],
    use_playwright: bool = False,
) -> RawFetch:
    timestamp = _now_ist()
    is_pdf = source_type == "pdf"

    if is_pdf:
        status, content, err = _fetch_static(url, is_pdf=True)
        method = "requests"
        content_type = "pdf"
    else:
        if use_playwright:
            status, content, err = _fetch_playwright(url)
            method = "playwright"
        else:
            status, content, err = _fetch_static(url)
            method = "requests"
            # Auto-upgrade to Playwright if content too short
            if (
                status == 200
                and content is not None
                and len(content) < MIN_HTML_CHARS
            ):
                logger.info(f"{fund_id}: static content short ({len(content)} chars), retrying with Playwright")
                status, content, err = _fetch_playwright(url)
                method = "playwright"
        content_type = "html"

    # Validate content size
    content_len = len(content) if content else 0
    min_size = MIN_PDF_BYTES if is_pdf else MIN_HTML_CHARS

    success = (
        status == 200
        and content is not None
        and content_len >= min_size
        and err is None
    )

    if not success and err is None:
        if status != 200:
            err = f"HTTP {status}"
        elif content_len < min_size:
            err = f"Content too short: {content_len} {'bytes' if is_pdf else 'chars'} (min {min_size})"

    if not success:
        logger.warning(f"{fund_id} | {url} | FAILED: {err}")
    else:
        logger.info(f"{fund_id} | {url} | OK ({content_len} {'bytes' if is_pdf else 'chars'}, {method})")

    return RawFetch(
        fund_id=fund_id,
        url=url,
        source_type=source_type,
        content_type=content_type,
        raw_content=content or (b"" if is_pdf else ""),
        fetch_timestamp=timestamp,
        http_status=status,
        fetch_method=method,
        content_length=content_len,
        fetch_success=success,
        error_message=err,
    )
