"""Unit tests for Category and Product models."""

import pytest
from models.category import Category
from models.product import Product


class TestCategoryModel:
    def test_tablename(self):
        assert Category.__tablename__ == "categories"

    def test_required_columns(self):
        cols = {c.name for c in Category.__table__.columns}
        assert {"id", "name", "description"}.issubset(cols)

    def test_name_is_unique(self):
        assert Category.__table__.columns["name"].unique

    def test_description_is_nullable(self):
        assert Category.__table__.columns["description"].nullable

    def test_name_is_not_nullable(self):
        assert not Category.__table__.columns["name"].nullable

    def test_instantiation(self):
        cat = Category(name="Military", description="War sets")
        assert cat.name == "Military"
        assert cat.description == "War sets"

    def test_instantiation_without_description(self):
        cat = Category(name="Space")
        assert cat.name == "Space"
        assert cat.description is None


class TestProductModel:
    def test_tablename(self):
        assert Product.__tablename__ == "products"

    def test_required_columns(self):
        cols = {c.name for c in Product.__table__.columns}
        required = {
            "id", "name", "description", "manufacturer",
            "piece_count", "min_age", "base_price",
            "stock_quantity", "image_url", "category_id",
        }
        assert required.issubset(cols)

    def test_stock_quantity_default_zero(self):
        col = Product.__table__.columns["stock_quantity"]
        assert col.default.arg == 0

    def test_category_id_is_nullable(self):
        assert Product.__table__.columns["category_id"].nullable

    def test_min_age_is_nullable(self):
        assert Product.__table__.columns["min_age"].nullable

    def test_description_is_nullable(self):
        assert Product.__table__.columns["description"].nullable

    def test_image_url_is_nullable(self):
        assert Product.__table__.columns["image_url"].nullable

    def test_name_is_not_nullable(self):
        assert not Product.__table__.columns["name"].nullable

    def test_manufacturer_is_not_nullable(self):
        assert not Product.__table__.columns["manufacturer"].nullable

    def test_base_price_is_not_nullable(self):
        assert not Product.__table__.columns["base_price"].nullable

    def test_category_fk_references_categories(self):
        fk = list(Product.__table__.columns["category_id"].foreign_keys)[0]
        assert "categories" in fk.target_fullname

    def test_name_is_indexed(self):
        indexed = {list(i.columns)[0].name for i in Product.__table__.indexes}
        assert "name" in indexed

    def test_manufacturer_is_indexed(self):
        indexed = {list(i.columns)[0].name for i in Product.__table__.indexes}
        assert "manufacturer" in indexed

    def test_instantiation(self):
        p = Product(
            name="COBI Panzer IV",
            manufacturer="Cobi",
            piece_count=500,
            min_age=8,
            base_price=89.99,
            stock_quantity=20,
        )
        assert p.name == "COBI Panzer IV"
        assert p.manufacturer == "Cobi"
        assert p.piece_count == 500
        assert p.base_price == 89.99

    def test_instantiation_minimal(self):
        p = Product(name="Test Set", manufacturer="Brand", piece_count=100, base_price=49.99)
        assert p.category_id is None
        assert p.image_url is None
        assert p.min_age is None


class TestSeedCatalog:
    def test_seed_catalog_skips_if_exists(self):
        from unittest.mock import MagicMock
        import seed

        db = MagicMock()
        db.query.return_value.first.return_value = MagicMock()  # already seeded

        seed.seed_catalog(db)

        db.add_all.assert_not_called()
        db.commit.assert_not_called()

    def test_seed_catalog_creates_categories_and_products(self):
        from unittest.mock import MagicMock, call
        import seed

        db = MagicMock()
        db.query.return_value.first.return_value = None  # not seeded yet

        # flush() must assign ids; simulate by setting id on flushed objects
        def fake_add_all(items):
            for i, item in enumerate(items, start=1):
                item.id = i

        db.add_all.side_effect = fake_add_all
        db.flush.side_effect = lambda: None

        seed.seed_catalog(db)

        assert db.add_all.call_count == 2  # once for categories, once for products
        db.commit.assert_called_once()
