from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class ScraperConfig:
    """
    Central configuration object for the scraping system.
    Supports environment variable overrides.
    """

    # Base scraping settings
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "SCRAPER_BASE_URL",
            "https://quotes.toscrape.com"
        )
    )

    delay: float = field(
        default_factory=lambda: float(
            os.getenv("SCRAPER_DELAY", "1.0")
        )
    )

    default_limit: int = field(
        default_factory=lambda: int(
            os.getenv("SCRAPER_DEFAULT_LIMIT", "20")
        )
    )

    # Export settings
    csv_filename: str = field(
        default_factory=lambda: os.getenv(
            "SCRAPER_CSV_FILE",
            "posts.csv"
        )
    )

    json_filename: str = field(
        default_factory=lambda: os.getenv(
            "SCRAPER_JSON_FILE",
            "posts.json"
        )
    )

    db_filename: str = field(
        default_factory=lambda: os.getenv(
            "SCRAPER_DB_FILE",
            "posts.db"
        )
    )

    # Logging level
    log_level: str = field(
        default_factory=lambda: os.getenv(
            "SCRAPER_LOG_LEVEL",
            "INFO"
        )
    )

    def __post_init__(self) -> None:
        self._validate()

    # ==============================
    # Validation
    # ==============================

    def _validate(self) -> None:
        if not isinstance(self.base_url, str) or not self.base_url.startswith("http"):
            raise ValueError("Invalid base_url configuration.")

        if self.delay < 0:
            raise ValueError("Delay must be non-negative.")

        if self.default_limit <= 0:
            raise ValueError("default_limit must be greater than 0.")

        if self.log_level.upper() not in {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }:
            raise ValueError("Invalid log level provided.")