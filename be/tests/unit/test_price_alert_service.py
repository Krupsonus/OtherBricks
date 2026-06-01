"""Unit tests for price alert service and schemas."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from models.price_alert import PriceAlert
from models.product import Product
from schemas.price_alert import PriceAlertCreate, PriceAlertOut
from services.price_alert_service import (
    _enrich,
    create_alert,
    delete_alert,
    get_user_alerts,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_product(id=5, name="Tank Set"):
    p = MagicMock(spec=Product)
    p.id = id
    p.name = name
    return p


def _make_alert(id=1, user_id=1, product_id=5, target_price="49.99"):
    a = MagicMock(spec=PriceAlert)
    a.id = id
    a.user_id = user_id
    a.product_id = product_id
    a.target_price = Decimal(target_price)
    a.created_at = datetime(2025, 6, 1, tzinfo=timezone.utc)
    a.product = _make_product(id=product_id)
    return a


def _db_returns(first=None, all_results=None, scalar=None):
    db = MagicMock()
    q = db.query.return_value
    q.options.return_value = q
    q.filter.return_value = q
    q.order_by.return_value = q
    q.group_by.return_value = q
    q.first.return_value = first
    q.all.return_value = all_results if all_results is not None else (
        [first] if first else []
    )
    q.scalar.return_value = scalar
    return db


# ---------------------------------------------------------------------------
# _enrich helper
# ---------------------------------------------------------------------------

class TestEnrich:
    def test_triggered_when_best_price_at_or_below_target(self):
        alert = _make_alert(target_price="50.00")
        result = _enrich(alert, Decimal("49.99"))
        assert result["is_triggered"] is True

    def test_triggered_when_best_price_equals_target(self):
        alert = _make_alert(target_price="50.00")
        result = _enrich(alert, Decimal("50.00"))
        assert result["is_triggered"] is True

    def test_not_triggered_when_best_price_above_target(self):
        alert = _make_alert(target_price="50.00")
        result = _enrich(alert, Decimal("50.01"))
        assert result["is_triggered"] is False

    def test_not_triggered_when_no_offers(self):
        alert = _make_alert(target_price="50.00")
        result = _enrich(alert, None)
        assert result["is_triggered"] is False
        assert result["best_offer_price"] is None

    def test_product_name_included(self):
        alert = _make_alert()
        result = _enrich(alert, None)
        assert result["product_name"] == "Tank Set"


# ---------------------------------------------------------------------------
# get_user_alerts
# ---------------------------------------------------------------------------

class TestGetUserAlerts:
    def test_returns_empty_when_no_alerts(self):
        db = _db_returns(all_results=[])
        result = get_user_alerts(db, user_id=1)
        assert result == []

    def test_returns_enriched_alerts(self):
        alert = _make_alert(target_price="60.00")
        db = MagicMock()

        alert_query = MagicMock()
        alert_query.options.return_value = alert_query
        alert_query.filter.return_value = alert_query
        alert_query.order_by.return_value = alert_query
        alert_query.all.return_value = [alert]

        offer_query = MagicMock()
        offer_query.filter.return_value = offer_query
        offer_query.group_by.return_value = offer_query
        offer_query.all.return_value = [(5, Decimal("55.00"))]

        db.query.side_effect = [alert_query, offer_query]

        result = get_user_alerts(db, user_id=1)
        assert len(result) == 1
        assert result[0].best_offer_price == 55.0
        assert result[0].is_triggered is True

    def test_not_triggered_when_offer_above_target(self):
        alert = _make_alert(target_price="40.00")
        db = MagicMock()

        alert_query = MagicMock()
        alert_query.options.return_value = alert_query
        alert_query.filter.return_value = alert_query
        alert_query.order_by.return_value = alert_query
        alert_query.all.return_value = [alert]

        offer_query = MagicMock()
        offer_query.filter.return_value = offer_query
        offer_query.group_by.return_value = offer_query
        offer_query.all.return_value = [(5, Decimal("55.00"))]

        db.query.side_effect = [alert_query, offer_query]

        result = get_user_alerts(db, user_id=1)
        assert result[0].is_triggered is False


# ---------------------------------------------------------------------------
# create_alert
# ---------------------------------------------------------------------------

class TestCreateAlert:
    def _payload(self, product_id=5, target_price=49.99):
        return PriceAlertCreate(product_id=product_id, target_price=target_price)

    def test_raises_404_when_product_not_found(self):
        from fastapi import HTTPException
        db = _db_returns(first=None)
        with pytest.raises(HTTPException) as exc:
            create_alert(db, user_id=1, payload=self._payload())
        assert exc.value.status_code == 404

    def test_commits_and_returns_alert_out(self):
        product = _make_product()
        alert = _make_alert()
        db = _db_returns(first=product, scalar=Decimal("45.00"))
        db.refresh.side_effect = lambda o: None

        with patch("services.price_alert_service.PriceAlert", return_value=alert):
            result = create_alert(db, user_id=1, payload=self._payload())

        db.commit.assert_called_once()
        assert isinstance(result, PriceAlertOut)

    def test_raises_409_on_duplicate(self):
        from fastapi import HTTPException
        from sqlalchemy.exc import IntegrityError

        product = _make_product()
        db = _db_returns(first=product)
        db.commit.side_effect = IntegrityError("", {}, Exception())

        alert = _make_alert()
        with patch("services.price_alert_service.PriceAlert", return_value=alert):
            with pytest.raises(HTTPException) as exc:
                create_alert(db, user_id=1, payload=self._payload())
        assert exc.value.status_code == 409
        db.rollback.assert_called_once()

    def test_is_triggered_true_when_offer_below_target(self):
        product = _make_product()
        alert = _make_alert(target_price="50.00")
        db = _db_returns(first=product, scalar=Decimal("40.00"))
        db.refresh.side_effect = lambda o: None

        with patch("services.price_alert_service.PriceAlert", return_value=alert):
            result = create_alert(db, user_id=1, payload=self._payload(target_price=50.00))

        assert result.is_triggered is True

    def test_is_triggered_false_when_no_offers(self):
        product = _make_product()
        alert = _make_alert(target_price="50.00")
        db = _db_returns(first=product, scalar=None)
        db.refresh.side_effect = lambda o: None

        with patch("services.price_alert_service.PriceAlert", return_value=alert):
            result = create_alert(db, user_id=1, payload=self._payload())

        assert result.is_triggered is False
        assert result.best_offer_price is None


# ---------------------------------------------------------------------------
# delete_alert
# ---------------------------------------------------------------------------

class TestDeleteAlert:
    def test_deletes_when_found(self):
        alert = _make_alert()
        db = _db_returns(first=alert)

        delete_alert(db, alert_id=1, user_id=1)

        db.delete.assert_called_once_with(alert)
        db.commit.assert_called_once()

    def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        db = _db_returns(first=None)

        with pytest.raises(HTTPException) as exc:
            delete_alert(db, alert_id=999, user_id=1)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TestPriceAlertSchemas:
    def test_target_price_must_be_positive(self):
        with pytest.raises(Exception):
            PriceAlertCreate(product_id=1, target_price=0)

    def test_target_price_negative_rejected(self):
        with pytest.raises(Exception):
            PriceAlertCreate(product_id=1, target_price=-5.0)

    def test_valid_create(self):
        pa = PriceAlertCreate(product_id=3, target_price=29.99)
        assert pa.target_price == 29.99

    def test_out_stringifies_datetime(self):
        dt = datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc)
        out = PriceAlertOut(
            id=1, product_id=3, product_name="Tank",
            target_price=50.0, best_offer_price=45.0,
            is_triggered=True, created_at=dt,
        )
        assert "2025-06-01" in out.created_at

    def test_out_accepts_string_date(self):
        out = PriceAlertOut(
            id=1, product_id=3, product_name="Tank",
            target_price=50.0, best_offer_price=None,
            is_triggered=False, created_at="2025-06-01T00:00:00+00:00",
        )
        assert "2025-06-01" in out.created_at
