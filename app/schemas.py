from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import Optional, List


# =========================================================
# Base Configuration
# =========================================================

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,   # ORM compatibility
        extra="forbid",         # Reject unexpected fields
        str_strip_whitespace=True
    )


# =========================================================
# Post Schemas
# =========================================================

class PostBase(BaseSchema):
    title: str = Field(..., min_length=3, max_length=255)
    url: HttpUrl
    content: Optional[str] = Field(None, max_length=10000)


class PostCreate(PostBase):
    """
    Schema for creating a new post.
    """
    pass


class PostUpdate(BaseSchema):
    """
    Schema for updating an existing post.
    All fields optional.
    """
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    url: Optional[HttpUrl] = None
    content: Optional[str] = Field(None, max_length=10000)


class PostResponse(PostBase):
    """
    Schema returned to client.
    """
    id: int


# =========================================================
# Pagination Schema
# =========================================================

class PaginationResponse(BaseSchema):
    total: int
    skip: int
    limit: int
    data: List[PostResponse]