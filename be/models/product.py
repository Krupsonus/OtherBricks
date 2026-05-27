from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Product(Base):
    """A construction brick set available in the catalogue.

    base_price is the portal's own selling price.
    External shop prices live in the PriceOffer model (added in F-02).
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    piece_count: Mapped[int] = mapped_column(Integer, nullable=False)
    min_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True, index=True
    )

    category: Mapped["Category | None"] = relationship("Category", back_populates="products")
    price_offers: Mapped[list["PriceOffer"]] = relationship(  # noqa: F821
        "PriceOffer", back_populates="product", cascade="all, delete-orphan"
    )
