"""Pydantic schemas for orders."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CartItemIn(BaseModel):
    """Single product line submitted in a checkout request."""
    product_id: int
    quantity: int = Field(ge=1)


class OrderCreateIn(BaseModel):
    """Payload for POST /orders."""
    items: list[CartItemIn] = Field(min_length=1)
    shipping_address: str = Field(min_length=5)
    payment_method: str = Field(default="stripe")


class OrderItemOut(BaseModel):
    """Single line item in an order response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: float


class OrderOut(BaseModel):
    """Full order response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total_amount: float
    shipping_address: str
    payment_method: str
    created_at: str
    items: list[OrderItemOut]

    @field_validator("created_at", mode="before")
    @classmethod
    def stringify_dt(cls, v: datetime | str) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)
