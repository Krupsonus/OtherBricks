"""Pydantic schemas for product reviews."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewCreate(BaseModel):
    """Payload for POST /products/{id}/reviews."""
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class ReviewOut(BaseModel):
    """Public representation of a product review."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    rating: int
    comment: str | None
    created_at: str
    author_name: str = ""

    @field_validator("created_at", mode="before")
    @classmethod
    def stringify_dt(cls, v: datetime | str) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)
