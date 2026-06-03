"""Pydantic schemas for admin-only endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.order import OrderOut


class ProductCreateIn(BaseModel):
    """Payload for admin POST /admin/products."""
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    manufacturer: str = Field(min_length=1, max_length=100)
    piece_count: int = Field(ge=1)
    min_age: int | None = Field(default=None, ge=0)
    base_price: float = Field(gt=0)
    stock_quantity: int = Field(ge=0, default=0)
    image_url: str | None = None
    category_id: int | None = None


class ProductUpdateIn(BaseModel):
    """Payload for admin PUT /admin/products/{id}. All fields optional."""
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    manufacturer: str | None = Field(default=None, min_length=1, max_length=100)
    piece_count: int | None = Field(default=None, ge=1)
    min_age: int | None = Field(default=None, ge=0)
    base_price: float | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    category_id: int | None = None


class UserAdminOut(BaseModel):
    """User representation for the admin panel."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: str

    @field_validator("created_at", mode="before")
    @classmethod
    def stringify_dt(cls, v: datetime | str) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)


class AdminOrderOut(OrderOut):
    """Order representation for the admin panel — includes user_id."""
    user_id: int
