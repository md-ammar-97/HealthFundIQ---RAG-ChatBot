import logging
import os
from config.settings import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
        # File handler for ingestion logs
        os.makedirs("logs", exist_ok=True)
        fh = logging.FileHandler(f"logs/{name.split('.')[-1]}.log")
        fh.setFormatter(handler.formatter)
        logger.addHandler(fh)
    return logger
