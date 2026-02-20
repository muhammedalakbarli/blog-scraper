from __future__ import annotations

import httpx
from typing import Optional


class ScraperClient:
    """
    Async HTTP client for fetching pages.
    Uses connection pooling for performance.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ScraperClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=10.0,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client:
            await self._client.aclose()

    async def fetch_page(self, page: int) -> str:
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        response = await self._client.get(f"/page/{page}/")
        response.raise_for_status()
        return response.text