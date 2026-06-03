"""Unit tests for admin service and schemas."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from models.category import Category
from models.order import Order
from models.product import Product
from models.user import User
from schemas.admin import AdminOrderOut, ProductCreateIn, ProductUpdateIn, UserAdminOut
from services.admin_service import (
    create_product,
    delete_product,
    get_all_orders,
    get_all_products,
    get_all_users,
    update_product,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_product(id=1, name="Tank"):
    p = MagicMock(spec=Product)
    p.id = id
    p.name = name
    p.description = None
    p.manufacturer = "COBI"
    p.piece_count = 200
    p.min_age = 8
    p.base_price = Decimal("49.99")
    p.stock_quantity = 10
    p.image_url = None
    p.category_id = None
    p.category = None
    p.updated_at = None
    return p


def _q(db, results=None, first=None):
    q = db.query.return_value
    q.options.return_value = q
    q.filter.return_value = q
    q.order_by.return_value = q
    q.all.return_value = results or []
    q.first.return_value = first
    return db


# ---------------------------------------------------------------------------
# get_all_products
# ---------------------------------------------------------------------------

class TestGetAllProducts:
    def test_returns_all_products(self):
        p = _make_product()
        db = MagicMock()
        _q(db, results=[p])
        assert get_all_products(db) == [p]

    def test_returns_empty(self):
        db = MagicMock()
        _q(db, results=[])
        assert get_all_products(db) == []


# ---------------------------------------------------------------------------
# create_product
# ---------------------------------------------------------------------------

class TestCreateProduct:
    def _payload(self, **kwargs):
        defaults = dict(name="New Set", manufacturer="COBI", piece_count=100,
                        base_price=39.99, stock_quantity=5)
        defaults.update(kwargs)
        return ProductCreateIn(**defaults)

    def test_commits_and_returns_product(self):
        product = _make_product()
        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        with patch("services.admin_service.Product", return_value=product):
            result = create_product(db, self._payload())

        db.add.assert_called_once_with(product)
        db.commit.assert_called_once()
        assert result is product

    def test_raises_404_when_category_not_found(self):
        from fastapi import HTTPException
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.first.return_value = None  # category not found

        with pytest.raises(HTTPException) as exc:
            create_product(db, self._payload(category_id=999))
        assert exc.value.status_code == 404

    def test_no_category_check_when_category_id_is_none(self):
        product = _make_product()
        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        with patch("services.admin_service.Product", return_value=product):
            create_product(db, self._payload(category_id=None))

        # Should not have queried Category at all
        db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# update_product
# ---------------------------------------------------------------------------

class TestUpdateProduct:
    def test_updates_provided_fields(self):
        product = _make_product()
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.first.return_value = product
        db.refresh.side_effect = lambda o: None

        result = update_product(db, product_id=1,
                                payload=ProductUpdateIn(name="Updated Name", stock_quantity=99))

        assert product.name == "Updated Name"
        assert product.stock_quantity == 99
        db.commit.assert_called_once()
        assert result is product

    def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            update_product(db, product_id=999, payload=ProductUpdateIn(name="X"))
        assert exc.value.status_code == 404

    def test_does_not_set_unspecified_fields(self):
        product = _make_product()
        product.base_price = Decimal("50.00")
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.first.return_value = product
        db.refresh.side_effect = lambda o: None

        update_product(db, product_id=1, payload=ProductUpdateIn(name="Only name"))

        # base_price not in payload → should not have changed
        assert product.base_price == Decimal("50.00")


# ---------------------------------------------------------------------------
# delete_product
# ---------------------------------------------------------------------------

class TestDeleteProduct:
    def test_deletes_when_found(self):
        product = _make_product()
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.first.return_value = product

        delete_product(db, product_id=1)

        db.delete.assert_called_once_with(product)
        db.commit.assert_called_once()

    def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            delete_product(db, product_id=999)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# get_all_orders / get_all_users
# ---------------------------------------------------------------------------

class TestGetAllOrders:
    def test_returns_orders(self):
        order = MagicMock(spec=Order)
        db = MagicMock()
        _q(db, results=[order])
        assert get_all_orders(db) == [order]


class TestGetAllUsers:
    def test_returns_users(self):
        user = MagicMock(spec=User)
        db = MagicMock()
        _q(db, results=[user])
        assert get_all_users(db) == [user]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TestAdminSchemas:
    def test_product_create_rejects_zero_price(self):
        with pytest.raises(Exception):
            ProductCreateIn(name="X", manufacturer="Y", piece_count=10, base_price=0)

    def test_product_create_rejects_zero_piece_count(self):
        with pytest.raises(Exception):
            ProductCreateIn(name="X", manufacturer="Y", piece_count=0, base_price=10)

    def test_product_update_all_optional(self):
        p = ProductUpdateIn()
        assert p.name is None
        assert p.base_price is None

    def test_product_update_rejects_negative_stock(self):
        with pytest.raises(Exception):
            ProductUpdateIn(stock_quantity=-1)

    def test_user_admin_out_stringifies_datetime(self):
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "a@b.com"
        user.first_name = "Jan"
        user.last_name = "Kowalski"
        user.role = "admin"
        user.is_active = True
        user.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        out = UserAdminOut.model_validate(user)
        assert "2025-01-01" in out.created_at

    def test_admin_order_out_includes_user_id(self):
        order = MagicMock(spec=Order)
        order.id = 1
        order.user_id = 5
        order.status = "paid"
        order.total_amount = Decimal("99.99")
        order.shipping_address = "ul. Test 1"
        order.payment_method = "stripe"
        order.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        order.items = []
        out = AdminOrderOut.model_validate(order)
        assert out.user_id == 5
