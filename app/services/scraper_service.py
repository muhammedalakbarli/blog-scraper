import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ..models import Post


async def scrape_and_save(url: str, db: Session):
    existing = db.query(Post).filter(Post.url == url).first()
    if existing:
        return existing

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string if soup.title else "No title found"

    post = Post(
        title=title,
        url=url,
        content=None
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post