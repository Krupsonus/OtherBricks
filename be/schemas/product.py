from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryOut(BaseModel):
    """Public representation of a product category."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class ProductOut(BaseModel):
    """Public representation of a product in the catalogue."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    manufacturer: str
    piece_count: int
    min_age: int | None
    base_price: float
    stock_quantity: int
    image_url: str | None
    category_id: int | None
    category: CategoryOut | None
    updated_at: str | None = None

    @field_validator("updated_at", mode="before")
    @classmethod
    def stringify_updated_at(cls, v: datetime | str | None) -> str | None:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v) if v is not None else None


class ProductListResponse(BaseModel):
    """Paginated list of products."""
    items: list[ProductOut]
    total: int
    limit: int
    offset: int


class PriceOfferOut(BaseModel):
    """External shop price offer for a product."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    shop_name: str
    shop_url: str
    price: float
    updated_at: str

    @field_validator("updated_at", mode="before")
    @classmethod
    def stringify_dt(cls, v: datetime | str) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)
