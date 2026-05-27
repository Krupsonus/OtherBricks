"""Unit tests for the PriceOffer model."""

from models.price_offer import PriceOffer


class TestPriceOfferModel:
    def test_tablename(self):
        assert PriceOffer.__tablename__ == "price_offers"

    def test_required_columns(self):
        cols = {c.name for c in PriceOffer.__table__.columns}
        assert {"id", "product_id", "shop_name", "shop_url", "price", "updated_at"}.issubset(cols)

    def test_product_id_is_not_nullable(self):
        assert not PriceOffer.__table__.columns["product_id"].nullable

    def test_shop_name_is_not_nullable(self):
        assert not PriceOffer.__table__.columns["shop_name"].nullable

    def test_shop_url_is_not_nullable(self):
        assert not PriceOffer.__table__.columns["shop_url"].nullable

    def test_price_is_not_nullable(self):
        assert not PriceOffer.__table__.columns["price"].nullable

    def test_product_id_is_indexed(self):
        indexed = {list(i.columns)[0].name for i in PriceOffer.__table__.indexes}
        assert "product_id" in indexed

    def test_product_fk_references_products(self):
        fk = list(PriceOffer.__table__.columns["product_id"].foreign_keys)[0]
        assert "products" in fk.target_fullname

    def test_product_fk_cascade_delete(self):
        fk = list(PriceOffer.__table__.columns["product_id"].foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_instantiation(self):
        offer = PriceOffer(
            product_id=1,
            shop_name="BrickShop",
            shop_url="https://brickshop.example.com/product/123",
            price=79.99,
        )
        assert offer.product_id == 1
        assert offer.shop_name == "BrickShop"
        assert offer.price == 79.99

    def test_shop_name_max_length(self):
        assert PriceOffer.__table__.columns["shop_name"].type.length == 120

    def test_shop_url_max_length(self):
        assert PriceOffer.__table__.columns["shop_url"].type.length == 512
