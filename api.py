from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from .database import get_db
from .models import Post
from .schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    PaginationResponse,
)
from .routers import scraper_router

# =========================================================
# Logging Configuration
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# =========================================================
# FastAPI App
# =========================================================

app = FastAPI(
    title="Blog Scraper API",
    version="1.0.0",
    description="Production-ready Blog Scraper Backend with PostgreSQL",
)

# =========================================================
# Rate Limiting
# =========================================================

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Slow down."},
    )


# =========================================================
# Database Dependency
# =========================================================

# =========================================================
# Startup Event
# =========================================================

@app.on_event("startup")
def startup():
    logger.info("Application started successfully.")


# =========================================================
# Routers
# =========================================================

app.include_router(scraper_router.router)

# =========================================================
# Health Check
# =========================================================

@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy"}


# =========================================================
# Create Post
# =========================================================

@app.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Posts"],
)
@limiter.limit("10/minute")
def create_post(
    request: Request,
    post: PostCreate,
    db: Session = Depends(get_db),
):
    try:
        new_post = Post(**post.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        logger.info(f"Post created with ID {new_post.id}")
        return new_post

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during create_post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )


# =========================================================
# Get All Posts (Pagination)
# =========================================================

@app.get(
    "/posts",
    response_model=PaginationResponse,
    tags=["Posts"],
)
def get_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    try:
        total = db.query(Post).count()
        posts = db.query(Post).offset(skip).limit(limit).all()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": posts,
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error during get_posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )


# =========================================================
# Get Single Post
# =========================================================

@app.get(
    "/posts/{post_id}",
    response_model=PostResponse,
    tags=["Posts"],
)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


# =========================================================
# Update Post
# =========================================================

@app.put(
    "/posts/{post_id}",
    response_model=PostResponse,
    tags=["Posts"],
)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    update_data = post_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(post, key, value)

    try:
        db.commit()
        db.refresh(post)
        logger.info(f"Post {post_id} updated")
        return post

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during update_post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )


# =========================================================
# Delete Post
# =========================================================

@app.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Posts"],
)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    try:
        db.delete(post)
        db.commit()
        logger.info(f"Post {post_id} deleted")
        return

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during delete_post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )