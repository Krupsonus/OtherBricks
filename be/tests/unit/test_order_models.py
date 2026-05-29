"""Unit tests for Order and OrderItem models."""

from models.order import Order, OrderItem, OrderStatus


class TestOrderStatus:
    def test_all_statuses_defined(self):
        statuses = {s.value for s in OrderStatus}
        assert statuses == {"pending", "paid", "shipped", "delivered", "cancelled"}

    def test_is_string_enum(self):
        assert isinstance(OrderStatus.pending, str)


class TestOrderModel:
    def test_tablename(self):
        assert Order.__tablename__ == "orders"

    def test_required_columns(self):
        cols = {c.name for c in Order.__table__.columns}
        assert {"id", "user_id", "status", "total_amount",
                "shipping_address", "payment_method", "created_at"}.issubset(cols)

    def test_user_id_not_nullable(self):
        assert not Order.__table__.columns["user_id"].nullable

    def test_total_amount_not_nullable(self):
        assert not Order.__table__.columns["total_amount"].nullable

    def test_shipping_address_not_nullable(self):
        assert not Order.__table__.columns["shipping_address"].nullable

    def test_payment_method_not_nullable(self):
        assert not Order.__table__.columns["payment_method"].nullable

    def test_status_default_pending(self):
        assert Order.__table__.columns["status"].default.arg == OrderStatus.pending

    def test_user_id_is_indexed(self):
        indexed = {list(i.columns)[0].name for i in Order.__table__.indexes}
        assert "user_id" in indexed

    def test_user_fk_references_users(self):
        fk = list(Order.__table__.columns["user_id"].foreign_keys)[0]
        assert "users" in fk.target_fullname

    def test_user_fk_cascade_delete(self):
        fk = list(Order.__table__.columns["user_id"].foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_instantiation(self):
        order = Order(
            user_id=1,
            total_amount=199.99,
            shipping_address="123 Main St, Warsaw",
            payment_method="stripe",
            status=OrderStatus.pending,
        )
        assert order.user_id == 1
        assert order.total_amount == 199.99
        assert order.status == OrderStatus.pending


class TestOrderItemModel:
    def test_tablename(self):
        assert OrderItem.__tablename__ == "order_items"

    def test_required_columns(self):
        cols = {c.name for c in OrderItem.__table__.columns}
        assert {"id", "order_id", "product_id", "quantity", "unit_price"}.issubset(cols)

    def test_order_id_not_nullable(self):
        assert not OrderItem.__table__.columns["order_id"].nullable

    def test_product_id_not_nullable(self):
        assert not OrderItem.__table__.columns["product_id"].nullable

    def test_quantity_not_nullable(self):
        assert not OrderItem.__table__.columns["quantity"].nullable

    def test_unit_price_not_nullable(self):
        assert not OrderItem.__table__.columns["unit_price"].nullable

    def test_order_id_is_indexed(self):
        indexed = {list(i.columns)[0].name for i in OrderItem.__table__.indexes}
        assert "order_id" in indexed

    def test_product_id_is_indexed(self):
        indexed = {list(i.columns)[0].name for i in OrderItem.__table__.indexes}
        assert "product_id" in indexed

    def test_order_fk_cascade_delete(self):
        fk = list(OrderItem.__table__.columns["order_id"].foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_product_fk_restrict_delete(self):
        fk = list(OrderItem.__table__.columns["product_id"].foreign_keys)[0]
        assert fk.ondelete == "RESTRICT"

    def test_order_fk_references_orders(self):
        fk = list(OrderItem.__table__.columns["order_id"].foreign_keys)[0]
        assert "orders" in fk.target_fullname

    def test_product_fk_references_products(self):
        fk = list(OrderItem.__table__.columns["product_id"].foreign_keys)[0]
        assert "products" in fk.target_fullname

    def test_instantiation(self):
        item = OrderItem(order_id=1, product_id=5, quantity=2, unit_price=89.99)
        assert item.order_id == 1
        assert item.product_id == 5
        assert item.quantity == 2
        assert item.unit_price == 89.99
