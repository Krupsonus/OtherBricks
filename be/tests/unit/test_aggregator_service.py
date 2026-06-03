"""Unit tests for price aggregation service."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from services.aggregator_service import (
    check_and_notify_alerts,
    generate_mock_prices,
    run_aggregation,
    upsert_price_offer,
)


# ---------------------------------------------------------------------------
# generate_mock_prices
# ---------------------------------------------------------------------------

class TestGenerateMockPrices:
    def test_returns_three_shops(self):
        result = generate_mock_prices(100.0)
        assert len(result) == 3

    def test_prices_within_range(self):
        for _ in range(20):
            for _, _, price in generate_mock_prices(100.0):
                assert 70 <= price <= 130  # ±20% of 100 with margin

    def test_price_is_rounded_to_two_decimals(self):
        for _, _, price in generate_mock_prices(99.99):
            assert round(price, 2) == price

    def test_returns_shop_name_and_url(self):
        result = generate_mock_prices(50.0)
        for shop_name, shop_url, _ in result:
            assert isinstance(shop_name, str) and len(shop_name) > 0
            assert shop_url.startswith("http")


# ---------------------------------------------------------------------------
# upsert_price_offer
# ---------------------------------------------------------------------------

class TestUpsertPriceOffer:
    def test_updates_existing_offer(self):
        from models.price_offer import PriceOffer
        existing = MagicMock(spec=PriceOffer)
        existing.price = 50.0
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = existing

        result = upsert_price_offer(db, 1, "ShopA", "https://shopa.com", 45.0)

        assert existing.price == 45.0
        assert result is existing
        db.add.assert_not_called()

    def test_creates_new_offer_when_none_exists(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with patch("services.aggregator_service.PriceOffer") as MockOffer:
            mock_offer = MagicMock()
            MockOffer.return_value = mock_offer
            result = upsert_price_offer(db, 1, "ShopB", "https://shopb.com", 60.0)

        db.add.assert_called_once_with(mock_offer)
        assert result is mock_offer


# ---------------------------------------------------------------------------
# check_and_notify_alerts
# ---------------------------------------------------------------------------

class TestCheckAndNotifyAlerts:
    def test_returns_empty_when_no_product_ids(self):
        db = MagicMock()
        result = check_and_notify_alerts(db, [])
        assert result == []

    def test_creates_notification_when_triggered(self):
        from models.price_alert import PriceAlert
        from models.product import Product

        alert = MagicMock(spec=PriceAlert)
        alert.product_id = 1
        alert.user_id = 2
        alert.target_price = Decimal("100.00")
        alert.product = MagicMock(spec=Product)
        alert.product.name = "Test Set"

        db = MagicMock()
        db.query.return_value.options.return_value.filter.return_value.all.return_value = [alert]
        # min price query returns 80.0 — below target 100.0
        db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [(1, 80.0)]

        with patch("services.aggregator_service.Notification") as MockNotif:
            mock_notif = MagicMock()
            MockNotif.return_value = mock_notif
            result = check_and_notify_alerts(db, [1])

        db.add.assert_called_once_with(mock_notif)
        assert len(result) == 1

    def test_no_notification_when_price_above_target(self):
        from models.price_alert import PriceAlert
        from models.product import Product

        alert = MagicMock(spec=PriceAlert)
        alert.product_id = 1
        alert.user_id = 2
        alert.target_price = Decimal("50.00")
        alert.product = MagicMock(spec=Product)
        alert.product.name = "Expensive Set"

        db = MagicMock()
        db.query.return_value.options.return_value.filter.return_value.all.return_value = [alert]
        # min price is 80.0 — above target 50.0
        db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [(1, 80.0)]

        result = check_and_notify_alerts(db, [1])

        db.add.assert_not_called()
        assert result == []


# ---------------------------------------------------------------------------
# run_aggregation
# ---------------------------------------------------------------------------

class TestRunAggregation:
    def test_returns_stats_dict(self):
        from models.product import Product
        p = MagicMock(spec=Product)
        p.id = 1
        p.base_price = Decimal("100.00")

        db = MagicMock()
        db.query.return_value.all.return_value = [p]
        db.query.return_value.filter.return_value.first.return_value = None  # new offers
        db.query.return_value.options.return_value.filter.return_value.all.return_value = []
        db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []

        with patch("services.aggregator_service.PriceOffer"):
            result = run_aggregation(db)

        assert result["products_processed"] == 1
        assert result["offers_updated"] == 3  # 3 mock shops
        assert "ran_at" in result
        db.commit.assert_called_once()

    def test_rollback_not_called_on_success(self):
        from models.product import Product
        db = MagicMock()
        db.query.return_value.all.return_value = []
        db.query.return_value.options.return_value.filter.return_value.all.return_value = []

        run_aggregation(db)

        db.rollback.assert_not_called()


# ---------------------------------------------------------------------------
# NotificationOut schema
# ---------------------------------------------------------------------------

class TestNotificationOut:
    def test_validates_from_orm(self):
        from datetime import datetime, timezone
        from schemas.notification import NotificationOut

        notif = MagicMock()
        notif.id = 1
        notif.user_id = 5
        notif.type = "price_alert"
        notif.message = "Price dropped!"
        notif.is_sent = True
        notif.sent_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        notif.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        out = NotificationOut.model_validate(notif)
        assert out.user_id == 5
        assert "2026-01-01" in out.sent_at
        assert "2026-01-01" in out.created_at

    def test_sent_at_none_when_not_sent(self):
        from datetime import datetime, timezone
        from schemas.notification import NotificationOut

        notif = MagicMock()
        notif.id = 2
        notif.user_id = 3
        notif.type = "price_alert"
        notif.message = "Test"
        notif.is_sent = False
        notif.sent_at = None
        notif.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        out = NotificationOut.model_validate(notif)
        assert out.sent_at is None
