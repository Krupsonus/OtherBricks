"""WishList and WishListProduct models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

# Many-to-many association table — no extra columns needed
wish_list_products = Table(
    "wish_list_products",
    Base.metadata,
    Column("wish_list_id", Integer, ForeignKey("wish_lists.id", ondelete="CASCADE"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
)


class WishList(Base):
    """A named list of products saved by a user."""

    __tablename__ = "wish_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="wish_lists")  # noqa: F821
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        "Product", secondary=wish_list_products, lazy="selectin"
    )
