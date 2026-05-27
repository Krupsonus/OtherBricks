"""PriceOffer model — external shop price for a product."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class PriceOffer(Base):
    __tablename__ = "price_offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    shop_name: Mapped[str] = mapped_column(String(120))
    shop_url: Mapped[str] = mapped_column(String(512))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    product: Mapped["Product"] = relationship("Product", back_populates="price_offers")  # noqa: F821
