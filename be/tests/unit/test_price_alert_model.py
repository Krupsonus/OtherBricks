"""Unit tests for PriceAlert model."""

from decimal import Decimal

from models.price_alert import PriceAlert


class TestPriceAlertModel:
    def test_tablename(self):
        assert PriceAlert.__tablename__ == "price_alerts"

    def test_required_columns(self):
        cols = {c.name for c in PriceAlert.__table__.columns}
        assert {"id", "user_id", "product_id", "target_price", "created_at"}.issubset(cols)

    def test_target_price_not_nullable(self):
        assert not PriceAlert.__table__.columns["target_price"].nullable

    def test_user_id_not_nullable(self):
        assert not PriceAlert.__table__.columns["user_id"].nullable

    def test_product_id_not_nullable(self):
        assert not PriceAlert.__table__.columns["product_id"].nullable

    def test_user_id_indexed(self):
        indexed = {list(i.columns)[0].name for i in PriceAlert.__table__.indexes}
        assert "user_id" in indexed

    def test_product_id_indexed(self):
        indexed = {list(i.columns)[0].name for i in PriceAlert.__table__.indexes}
        assert "product_id" in indexed

    def test_user_fk_references_users(self):
        fk = list(PriceAlert.__table__.columns["user_id"].foreign_keys)[0]
        assert "users" in fk.target_fullname

    def test_product_fk_references_products(self):
        fk = list(PriceAlert.__table__.columns["product_id"].foreign_keys)[0]
        assert "products" in fk.target_fullname

    def test_user_fk_cascade_delete(self):
        fk = list(PriceAlert.__table__.columns["user_id"].foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_product_fk_cascade_delete(self):
        fk = list(PriceAlert.__table__.columns["product_id"].foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_unique_constraint_on_user_product(self):
        constraint_names = {c.name for c in PriceAlert.__table__.constraints}
        assert "uq_alert_user_product" in constraint_names

    def test_target_price_is_numeric(self):
        from sqlalchemy import Numeric
        col_type = PriceAlert.__table__.columns["target_price"].type
        assert isinstance(col_type, Numeric)

    def test_instantiation(self):
        alert = PriceAlert(user_id=1, product_id=3, target_price=Decimal("49.99"))
        assert alert.user_id == 1
        assert alert.product_id == 3
        assert alert.target_price == Decimal("49.99")
