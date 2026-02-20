from __future__ import annotations

import asyncio
import logging
from typing import List, Dict, Any

from .client import ScraperClient
from .parser import QuoteParser


class ScraperService:
    """
    Async business layer responsible for:
    - Coordinating page fetching
    - Applying concurrency limits
    - Parsing responses
    - Returning structured data
    """

    def __init__(
        self,
        client: ScraperClient,
        delay: float,
        max_concurrency: int = 5,
    ) -> None:
        self.client = client
        self.delay = delay
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def _fetch_and_parse(self, page: int) -> List[Dict[str, Any]]:
        """
        Fetch a single page and parse it.
        Concurrency controlled via semaphore.
        """

        async with self.semaphore:
            try:
                html = await self.client.fetch_page(page)
                parsed = QuoteParser.parse(html)
                self.logger.debug(f"Page {page} parsed successfully")
                return parsed

            except Exception as e:
                self.logger.error(f"Failed to process page {page}: {e}")
                return []

    async def scrape(self, limit: int) -> List[Dict[str, Any]]:
        """
        Main scraping orchestration method.
        Fetches multiple pages concurrently and
        returns up to `limit` records.
        """

        if limit <= 0:
            raise ValueError("Limit must be greater than zero.")

        collected: List[Dict[str, Any]] = []

        # quotes.toscrape.com has 10 quotes per page
        items_per_page = 10
        pages_needed = (limit // items_per_page) + 2

        self.logger.info(
            f"Scraping started | limit={limit} | pages={pages_needed}"
        )

        async with self.client:
            tasks = [
                self._fetch_and_parse(page)
                for page in range(1, pages_needed + 1)
            ]

            results = await asyncio.gather(*tasks)

            for page_data in results:
                for item in page_data:
                    collected.append(item)
                    if len(collected) >= limit:
                        break
                if len(collected) >= limit:
                    break

        self.logger.info(f"Scraping completed | records={len(collected)}")

        return collected