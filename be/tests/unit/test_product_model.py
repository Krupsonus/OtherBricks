"""Unit tests for Product model — focused on F-08 addition."""

from sqlalchemy import DateTime

from models.product import Product


class TestProductModel:
    def test_tablename(self):
        assert Product.__tablename__ == "products"

    def test_updated_at_column_exists(self):
        cols = {c.name for c in Product.__table__.columns}
        assert "updated_at" in cols

    def test_updated_at_is_nullable(self):
        assert Product.__table__.columns["updated_at"].nullable

    def test_updated_at_is_datetime_type(self):
        col_type = Product.__table__.columns["updated_at"].type
        assert isinstance(col_type, DateTime)

    def test_updated_at_has_onupdate(self):
        col = Product.__table__.columns["updated_at"]
        assert col.onupdate is not None

    def test_required_columns_still_present(self):
        cols = {c.name for c in Product.__table__.columns}
        assert {"id", "name", "manufacturer", "base_price", "stock_quantity"}.issubset(cols)
