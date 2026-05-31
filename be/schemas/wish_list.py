"""Pydantic schemas for wishlists."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.product import ProductOut


class WishListCreate(BaseModel):
    """Payload for POST /wishlists."""
    name: str = Field(min_length=1, max_length=100)


class WishListOut(BaseModel):
    """Full wishlist response with embedded products."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: str
    products: list[ProductOut]

    @field_validator("created_at", mode="before")
    @classmethod
    def stringify_dt(cls, v: datetime | str) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)
