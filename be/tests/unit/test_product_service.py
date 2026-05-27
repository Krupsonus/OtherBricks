"""Unit tests for product_service — DB calls are mocked."""

from unittest.mock import MagicMock, patch, call
import pytest

from models.product import Product
from models.category import Category
from services.product_service import (
    get_products,
    get_product_by_id,
    get_all_categories,
    MAX_PAGE_SIZE,
)


def _make_db(items=None, count=0):
    """Build a mock DB session that returns *items* from .all() and *count* from .count()."""
    db = MagicMock()
    q = db.query.return_value
    q.options.return_value = q
    q.filter.return_value = q
    q.offset.return_value = q
    q.limit.return_value = q
    q.order_by.return_value = q
    q.count.return_value = count
    q.all.return_value = items or []
    q.first.return_value = items[0] if items else None
    return db


class TestGetProducts:
    def test_returns_items_and_total(self):
        products = [MagicMock(spec=Product), MagicMock(spec=Product)]
        db = _make_db(products, count=2)
        items, total = get_products(db)
        assert len(items) == 2
        assert total == 2

    def test_empty_catalogue(self):
        db = _make_db([], count=0)
        items, total = get_products(db)
        assert items == []
        assert total == 0

    def test_limit_capped_at_max_page_size(self):
        db = _make_db([], count=0)
        get_products(db, limit=100)
        q = db.query.return_value.options.return_value
        q.limit.assert_called_with(MAX_PAGE_SIZE)

    def test_limit_respected_when_within_max(self):
        db = _make_db([], count=0)
        get_products(db, limit=5)
        q = db.query.return_value.options.return_value
        q.limit.assert_called_with(5)

    def test_offset_applied(self):
        db = _make_db([], count=0)
        get_products(db, offset=40)
        q = db.query.return_value.options.return_value
        q.offset.assert_called_with(40)

    def test_search_filter_applied(self):
        db = _make_db([], count=0)
        get_products(db, search="panzer")
        q = db.query.return_value.options.return_value
        q.filter.assert_called()

    def test_manufacturer_filter_applied(self):
        db = _make_db([], count=0)
        get_products(db, manufacturer="Cobi")
        q = db.query.return_value.options.return_value
        assert q.filter.called

    def test_no_filters_applied_when_none(self):
        db = _make_db([], count=0)
        get_products(db)
        q = db.query.return_value.options.return_value
        q.filter.assert_not_called()

    def test_category_filter_applied(self):
        db = _make_db([], count=0)
        get_products(db, category_id=1)
        q = db.query.return_value.options.return_value
        q.filter.assert_called()

    def test_min_price_filter_applied(self):
        db = _make_db([], count=0)
        get_products(db, min_price=50.0)
        q = db.query.return_value.options.return_value
        q.filter.assert_called()

    def test_max_price_filter_applied(self):
        db = _make_db([], count=0)
        get_products(db, max_price=200.0)
        q = db.query.return_value.options.return_value
        q.filter.assert_called()

    def test_min_pieces_filter_applied(self):
        db = _make_db([], count=0)
        get_products(db, min_pieces=300)
        q = db.query.return_value.options.return_value
        q.filter.assert_called()

    def test_max_pieces_filter_applied(self):
        db = _make_db([], count=0)
        get_products(db, max_pieces=1000)
        q = db.query.return_value.options.return_value
        q.filter.assert_called()

    def test_min_age_filter_applied(self):
        db = _make_db([], count=0)
        get_products(db, min_age=8)
        q = db.query.return_value.options.return_value
        q.filter.assert_called()


class TestGetProductById:
    def test_returns_product_when_found(self):
        product = MagicMock(spec=Product)
        db = _make_db([product])
        result = get_product_by_id(db, 1)
        assert result is product

    def test_returns_none_when_not_found(self):
        db = _make_db([])
        result = get_product_by_id(db, 999)
        assert result is None


class TestGetAllCategories:
    def test_returns_all_categories(self):
        cats = [MagicMock(spec=Category), MagicMock(spec=Category)]
        db = _make_db(cats)
        result = get_all_categories(db)
        assert result == cats

    def test_returns_empty_list_when_no_categories(self):
        db = _make_db([])
        result = get_all_categories(db)
        assert result == []

    def test_orders_by_name(self):
        db = _make_db([])
        get_all_categories(db)
        q = db.query.return_value
        q.order_by.assert_called_once()
