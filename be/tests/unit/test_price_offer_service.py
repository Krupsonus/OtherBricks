"""Unit tests for price offer service and schema."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from models.price_offer import PriceOffer
from schemas.product import PriceOfferOut
from services.product_service import get_price_offers


def _make_db(items=None):
    db = MagicMock()
    q = db.query.return_value
    q.filter.return_value = q
    q.order_by.return_value = q
    q.all.return_value = items or []
    return db


def _make_offer(**kwargs) -> MagicMock:
    defaults = dict(
        id=1,
        product_id=1,
        shop_name="BrickShop",
        shop_url="https://brickshop.example.com",
        price=79.99,
        updated_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    defaults.update(kwargs)
    offer = MagicMock(spec=PriceOffer)
    for k, v in defaults.items():
        setattr(offer, k, v)
    return offer


class TestGetPriceOffers:
    def test_returns_all_offers_for_product(self):
        offers = [_make_offer(id=1), _make_offer(id=2)]
        db = _make_db(offers)
        result = get_price_offers(db, product_id=1)
        assert result == offers

    def test_returns_empty_list_when_no_offers(self):
        db = _make_db([])
        result = get_price_offers(db, product_id=99)
        assert result == []

    def test_queries_correct_model(self):
        db = _make_db([])
        get_price_offers(db, product_id=1)
        db.query.assert_called_once_with(PriceOffer)

    def test_filters_by_product_id(self):
        db = _make_db([])
        get_price_offers(db, product_id=5)
        db.query.return_value.filter.assert_called_once()

    def test_orders_by_price(self):
        db = _make_db([])
        get_price_offers(db, product_id=1)
        db.query.return_value.filter.return_value.order_by.assert_called_once()


class TestPriceOfferOutSchema:
    def test_serialises_from_orm(self):
        offer = _make_offer(id=3, shop_name="TestShop", price=99.99)
        out = PriceOfferOut.model_validate(offer)
        assert out.id == 3
        assert out.shop_name == "TestShop"
        assert out.price == 99.99

    def test_updated_at_stringified_from_datetime(self):
        dt = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        offer = _make_offer(updated_at=dt)
        out = PriceOfferOut.model_validate(offer)
        assert "2025-06-15" in out.updated_at

    def test_updated_at_already_string_passthrough(self):
        offer = _make_offer(updated_at="2025-01-01T00:00:00+00:00")
        out = PriceOfferOut.model_validate(offer)
        assert "2025-01-01" in out.updated_at

    def test_shop_url_preserved(self):
        url = "https://example.com/product/42"
        offer = _make_offer(shop_url=url)
        out = PriceOfferOut.model_validate(offer)
        assert out.shop_url == url

    def test_price_is_float(self):
        offer = _make_offer(price=149.95)
        out = PriceOfferOut.model_validate(offer)
        assert isinstance(out.price, float)
