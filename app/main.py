from __future__ import annotations

import logging
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from scraper.config import ScraperConfig
from scraper.client import ScraperClient
from scraper.service import ScraperService


# ==========================================
# Logging Configuration
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("ScraperAPI")


# ==========================================
# FastAPI Application
# ==========================================

app = FastAPI(
    title="Blog Scraper API",
    version="1.0.0",
    description="Professional Modular Web Scraper System",
)


# ==========================================
# Dependency Factory
# ==========================================

def get_scraper_service(delay: float) -> ScraperService:
    config = ScraperConfig(delay=delay)
    client = ScraperClient(config.base_url)
    return ScraperService(client, config.delay)


# ==========================================
# Health Check
# ==========================================

@app.get("/health", tags=["System"])
def health_check() -> Dict[str, str]:
    return {"status": "healthy"}


# ==========================================
# Scrape Endpoint
# ==========================================

@app.get("/scrape", tags=["Scraper"])
def scrape_posts(
    limit: int = Query(20, ge=1, le=100),
    delay: float = Query(1.0, ge=0.0, le=10.0),
) -> JSONResponse:
    """
    Scrape blog posts and return collected data.
    """

    logger.info(f"Scrape request received | limit={limit}, delay={delay}")

    try:
        service = get_scraper_service(delay)
        data: List[Dict[str, Any]] = service.scrape(limit)

        if not data:
            logger.warning("No data collected.")
            return JSONResponse(
                status_code=204,
                content={"message": "No data collected."},
            )

        logger.info(f"Scrape completed | records={len(data)}")

        return JSONResponse(
            status_code=200,
            content={
                "total_records": len(data),
                "data": data,
            },
        )

    except Exception as e:
        logger.exception("Scraping failed.")
        raise HTTPException(
            status_code=500,
            detail="Internal scraping error.",
        )