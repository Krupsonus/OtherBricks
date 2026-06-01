"""Pydantic schemas for price alerts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PriceAlertCreate(BaseModel):
    """Payload for POST /alerts."""
    product_id: int
    target_price: float = Field(gt=0)


class PriceAlertOut(BaseModel):
    """Price alert with live triggered status."""
    model_config = ConfigDict(from_attributes=False)

    id: int
    product_id: int
    product_name: str
    target_price: float
    best_offer_price: float | None
    is_triggered: bool
    created_at: str

    @field_validator("created_at", mode="before")
    @classmethod
    def stringify_dt(cls, v: datetime | str) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)
