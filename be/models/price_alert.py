"""PriceAlert model — user-defined target price for a product."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class PriceAlert(Base):
    """A price threshold set by a user for a specific product.

    The alert is considered triggered when any external price offer
    for that product is at or below target_price.
    """

    __tablename__ = "price_alerts"

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_alert_user_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    target_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User")  # noqa: F821
    product: Mapped["Product"] = relationship("Product")  # noqa: F821
