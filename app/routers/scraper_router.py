from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.scraper_service import scrape_and_save

router = APIRouter(prefix="/scrape", tags=["Scraper"])


@router.post("/")
async def scrape(url: str, db: Session = Depends(get_db)):
    return await scrape_and_save(url, db)