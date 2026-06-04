"""
Daily ingestion is triggered by GitHub Actions cron (.github/workflows/daily-ingestion.yml).
This module is kept as a thin wrapper so the admin endpoint in api/router.py
can trigger a manual refresh via HTTP without APScheduler.
"""
import threading
from ingestion.logger import get_logger

logger = get_logger("scheduler.refresh")

_ingestion_lock = threading.Lock()
_ingestion_running = False


def run_daily_refresh() -> bool:
    """
    Run the full ingestion pipeline once.
    Returns True if ingestion started, False if already running.
    Thread-safe — concurrent calls are rejected via lock.
    """
    global _ingestion_running
    if not _ingestion_lock.acquire(blocking=False):
        logger.warning("Skipping refresh request — ingestion already running")
        return False

    try:
        _ingestion_running = True
        logger.info("Starting corpus refresh")
        from ingestion.run_ingestion import ingest_all
        ingest_all()
        logger.info("Corpus refresh complete")
        return True
    except Exception as e:
        logger.error(f"Corpus refresh failed: {e}", exc_info=True)
        return False
    finally:
        _ingestion_running = False
        _ingestion_lock.release()


def is_ingestion_running() -> bool:
    return _ingestion_running
