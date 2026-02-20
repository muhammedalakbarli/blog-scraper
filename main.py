from __future__ import annotations

import argparse
import logging
import sys
from typing import List, Dict, Any

from scraper.config import ScraperConfig
from scraper.client import ScraperClient
from scraper.service import ScraperService
from scraper.exporter import (
    CSVExporter,
    JSONExporter,
    SQLiteExporter,
)


# ==============================
# Logging Setup
# ==============================

def setup_logging(level: str) -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


# ==============================
# CLI Argument Parsing
# ==============================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Professional Modular Web Scraper System"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of records to scrape",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests (seconds)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )

    return parser.parse_args()


# ==============================
# Export Orchestration
# ==============================

def export_data(data: List[Dict[str, Any]]) -> None:
    exporters = [
        CSVExporter("posts.csv"),
        JSONExporter("posts.json"),
        SQLiteExporter("posts.db"),
    ]

    for exporter in exporters:
        exporter.export(data)


# ==============================
# Application Entry Logic
# ==============================

def run(limit: int, delay: float) -> None:
    logger = logging.getLogger("ScraperApp")

    config = ScraperConfig(delay=delay)
    client = ScraperClient(config.base_url)
    service = ScraperService(client, config.delay)

    logger.info("Scraping started...")

    try:
        data = service.scrape(limit)

        if not data:
            logger.warning("No data collected.")
            return

        export_data(data)

        logger.info("Export completed successfully.")
        logger.info(f"Total records exported: {len(data)}")

    except Exception as e:
        logger.exception("Application failed.")
        sys.exit(1)


# ==============================
# Main
# ==============================

def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)

    run(limit=args.limit, delay=args.delay)


if __name__ == "__main__":
    main()