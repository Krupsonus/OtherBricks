"""Unit tests for order service and schemas."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call
from decimal import Decimal

import pytest

from models.order import Order, OrderItem, OrderStatus
from models.product import Product
from schemas.order import CartItemIn, OrderCreateIn, OrderOut, OrderItemOut
from services.order_service import (
    create_order,
    get_user_orders,
    get_order,
    _mock_stripe_charge,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_product(id: int, name: str, price: float, stock: int) -> MagicMock:
    p = MagicMock(spec=Product)
    p.id = id
    p.name = name
    p.base_price = Decimal(str(price))
    p.stock_quantity = stock
    return p


def _make_db_with_products(products: list) -> MagicMock:
    db = MagicMock()
    product_map = {p.id: p for p in products}

    q = db.query.return_value
    q.options.return_value = q
    q.filter.return_value = q
    q.order_by.return_value = q
    q.all.return_value = products
    q.first.return_value = products[0] if products else None
    return db, product_map


# ---------------------------------------------------------------------------
# _mock_stripe_charge
# ---------------------------------------------------------------------------

class TestMockStripeCharge:
    def test_returns_string(self):
        result = _mock_stripe_charge(99.99, "stripe")
        assert isinstance(result, str)

    def test_starts_with_pi_mock(self):
        result = _mock_stripe_charge(50.0, "stripe")
        assert result.startswith("pi_mock_")

    def test_different_amounts_produce_different_ids(self):
        a = _mock_stripe_charge(100.0, "stripe")
        b = _mock_stripe_charge(200.0, "stripe")
        assert a != b


# ---------------------------------------------------------------------------
# create_order
# ---------------------------------------------------------------------------

class TestCreateOrder:
    def _payload(self, items=None):
        return OrderCreateIn(
            items=items or [CartItemIn(product_id=1, quantity=2)],
            shipping_address="ul. Testowa 1, Warszawa",
            payment_method="stripe",
        )

    def test_raises_422_when_product_missing(self):
        from fastapi import HTTPException
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.all.return_value = []  # no products found

        with pytest.raises(HTTPException) as exc:
            create_order(db, user_id=1, payload=self._payload())
        assert exc.value.status_code == 422

    def test_raises_422_when_insufficient_stock(self):
        from fastapi import HTTPException
        product = _make_product(1, "Tank", 89.99, stock=1)
        db, _ = _make_db_with_products([product])

        payload = self._payload([CartItemIn(product_id=1, quantity=5)])
        with pytest.raises(HTTPException) as exc:
            create_order(db, user_id=1, payload=payload)
        assert exc.value.status_code == 422
        assert "Insufficient stock" in exc.value.detail

    def test_commits_on_success(self):
        product = _make_product(1, "Tank", 89.99, stock=10)
        db, _ = _make_db_with_products([product])

        order_mock = MagicMock(spec=Order)
        order_mock.id = 42
        order_mock.items = []

        db.flush.side_effect = lambda: setattr(order_mock, "id", 42)
        db.refresh.side_effect = lambda o: None

        with patch("services.order_service.Order", return_value=order_mock):
            create_order(db, user_id=1, payload=self._payload())

        db.commit.assert_called_once()

    def test_decrements_stock(self):
        product = _make_product(1, "Tank", 89.99, stock=10)
        db, _ = _make_db_with_products([product])

        order_mock = MagicMock(spec=Order)
        order_mock.id = 1
        order_mock.items = []
        db.refresh.side_effect = lambda o: None

        with patch("services.order_service.Order", return_value=order_mock):
            create_order(db, user_id=1, payload=self._payload([CartItemIn(product_id=1, quantity=3)]))

        assert product.stock_quantity == 7

    def test_order_status_is_paid(self):
        product = _make_product(1, "Tank", 89.99, stock=10)
        db, _ = _make_db_with_products([product])

        captured = {}

        def capture_order(**kwargs):
            captured.update(kwargs)
            m = MagicMock(spec=Order)
            m.id = 1
            m.items = []
            return m

        db.refresh.side_effect = lambda o: None

        with patch("services.order_service.Order", side_effect=capture_order):
            create_order(db, user_id=1, payload=self._payload())

        assert captured.get("status") == OrderStatus.paid

    def test_total_calculated_correctly(self):
        product = _make_product(1, "Tank", 100.00, stock=10)
        db, _ = _make_db_with_products([product])

        captured = {}

        def capture_order(**kwargs):
            captured.update(kwargs)
            m = MagicMock(spec=Order)
            m.id = 1
            m.items = []
            return m

        db.refresh.side_effect = lambda o: None

        with patch("services.order_service.Order", side_effect=capture_order):
            create_order(db, user_id=1, payload=self._payload([CartItemIn(product_id=1, quantity=3)]))

        assert captured.get("total_amount") == 300.0

    def test_flushes_before_creating_items(self):
        product = _make_product(1, "Tank", 89.99, stock=10)
        db, _ = _make_db_with_products([product])

        order_mock = MagicMock(spec=Order)
        order_mock.id = 1
        order_mock.items = []
        db.refresh.side_effect = lambda o: None

        with patch("services.order_service.Order", return_value=order_mock):
            create_order(db, user_id=1, payload=self._payload())

        db.flush.assert_called_once()


# ---------------------------------------------------------------------------
# get_user_orders
# ---------------------------------------------------------------------------

class TestGetUserOrders:
    def test_returns_orders_for_user(self):
        orders = [MagicMock(spec=Order), MagicMock(spec=Order)]
        db = MagicMock()
        q = db.query.return_value
        q.options.return_value = q
        q.filter.return_value = q
        q.order_by.return_value = q
        q.all.return_value = orders

        result = get_user_orders(db, user_id=1)
        assert result == orders

    def test_returns_empty_when_no_orders(self):
        db = MagicMock()
        q = db.query.return_value
        q.options.return_value = q
        q.filter.return_value = q
        q.order_by.return_value = q
        q.all.return_value = []

        result = get_user_orders(db, user_id=99)
        assert result == []


# ---------------------------------------------------------------------------
# get_order
# ---------------------------------------------------------------------------

class TestGetOrder:
    def test_returns_order_when_found(self):
        order = MagicMock(spec=Order)
        db = MagicMock()
        q = db.query.return_value
        q.options.return_value = q
        q.filter.return_value = q
        q.first.return_value = order

        result = get_order(db, order_id=1, user_id=1)
        assert result is order

    def test_returns_none_when_not_found(self):
        db = MagicMock()
        q = db.query.return_value
        q.options.return_value = q
        q.filter.return_value = q
        q.first.return_value = None

        result = get_order(db, order_id=999, user_id=1)
        assert result is None


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TestOrderSchemas:
    def test_cart_item_quantity_must_be_at_least_1(self):
        with pytest.raises(Exception):
            CartItemIn(product_id=1, quantity=0)

    def test_order_create_requires_at_least_one_item(self):
        with pytest.raises(Exception):
            OrderCreateIn(items=[], shipping_address="ul. X 1", payment_method="stripe")

    def test_order_create_shipping_address_min_length(self):
        with pytest.raises(Exception):
            OrderCreateIn(
                items=[CartItemIn(product_id=1, quantity=1)],
                shipping_address="ab",
                payment_method="stripe",
            )

    def test_order_out_stringifies_datetime(self):
        dt = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        order = MagicMock(spec=Order)
        order.id = 1
        order.status = "paid"
        order.total_amount = 199.99
        order.shipping_address = "ul. Test 1"
        order.payment_method = "stripe"
        order.created_at = dt
        order.items = []
        out = OrderOut.model_validate(order)
        assert "2025-06-01" in out.created_at

    def test_order_item_out_fields(self):
        item = MagicMock(spec=OrderItem)
        item.id = 1
        item.product_id = 5
        item.quantity = 2
        item.unit_price = Decimal("89.99")
        out = OrderItemOut.model_validate(item)
        assert out.product_id == 5
        assert out.quantity == 2

    def test_order_out_accepts_string_created_at(self):
        order = MagicMock(spec=Order)
        order.id = 1
        order.status = "paid"
        order.total_amount = 50.0
        order.shipping_address = "ul. Test 1"
        order.payment_method = "stripe"
        order.created_at = "2025-06-01T12:00:00+00:00"
        order.items = []
        out = OrderOut.model_validate(order)
        assert "2025-06-01" in out.created_at
