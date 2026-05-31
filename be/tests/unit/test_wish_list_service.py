"""Unit tests for wishlist service and schemas."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from models.product import Product
from models.wish_list import WishList
from schemas.wish_list import WishListCreate, WishListOut
from services.wish_list_service import (
    add_product,
    create_wishlist,
    delete_wishlist,
    get_user_wishlists,
    remove_product,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_wishlist(id=1, user_id=1, name="My List", products=None):
    wl = MagicMock(spec=WishList)
    wl.id = id
    wl.user_id = user_id
    wl.name = name
    wl.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    wl.products = products if products is not None else []
    return wl


def _make_product(id=10):
    p = MagicMock(spec=Product)
    p.id = id
    p.name = "Test Brick"
    p.description = None
    p.manufacturer = "COBI"
    p.piece_count = 100
    p.min_age = None
    p.base_price = 49.99
    p.stock_quantity = 5
    p.image_url = None
    p.category_id = None
    p.category = None
    return p


def _single_query_db(first_return):
    """DB mock whose .query().filter().first() returns first_return."""
    db = MagicMock()
    q = db.query.return_value
    q.filter.return_value = q
    q.order_by.return_value = q
    q.all.return_value = [first_return] if first_return else []
    q.first.return_value = first_return
    return db


def _two_query_db(first_wl, second_product):
    """DB mock whose first query returns wl, second query returns product."""
    db = MagicMock()

    wl_query = MagicMock()
    wl_query.filter.return_value = wl_query
    wl_query.first.return_value = first_wl

    product_query = MagicMock()
    product_query.filter.return_value = product_query
    product_query.first.return_value = second_product

    db.query.side_effect = [wl_query, product_query]
    return db


# ---------------------------------------------------------------------------
# get_user_wishlists
# ---------------------------------------------------------------------------

class TestGetUserWishlists:
    def test_returns_wishlists_for_user(self):
        wl = _make_wishlist()
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.order_by.return_value = q
        q.all.return_value = [wl]

        result = get_user_wishlists(db, user_id=1)
        assert result == [wl]

    def test_returns_empty_list_when_none(self):
        db = MagicMock()
        q = db.query.return_value
        q.filter.return_value = q
        q.order_by.return_value = q
        q.all.return_value = []

        result = get_user_wishlists(db, user_id=99)
        assert result == []


# ---------------------------------------------------------------------------
# create_wishlist
# ---------------------------------------------------------------------------

class TestCreateWishlist:
    def test_commits_and_returns_wishlist(self):
        wl = _make_wishlist()
        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        with patch("services.wish_list_service.WishList", return_value=wl):
            result = create_wishlist(db, user_id=1, payload=WishListCreate(name="Favourites"))

        db.add.assert_called_once_with(wl)
        db.commit.assert_called_once()
        assert result is wl

    def test_passes_correct_name(self):
        captured = {}

        def capture(**kwargs):
            captured.update(kwargs)
            m = _make_wishlist(**{k: v for k, v in kwargs.items() if k in ("id", "user_id", "name")})
            return m

        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        with patch("services.wish_list_service.WishList", side_effect=capture):
            create_wishlist(db, user_id=2, payload=WishListCreate(name="Holiday picks"))

        assert captured.get("name") == "Holiday picks"
        assert captured.get("user_id") == 2


# ---------------------------------------------------------------------------
# delete_wishlist
# ---------------------------------------------------------------------------

class TestDeleteWishlist:
    def test_deletes_when_found(self):
        wl = _make_wishlist()
        db = _single_query_db(wl)

        delete_wishlist(db, wishlist_id=1, user_id=1)

        db.delete.assert_called_once_with(wl)
        db.commit.assert_called_once()

    def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        db = _single_query_db(None)

        with pytest.raises(HTTPException) as exc:
            delete_wishlist(db, wishlist_id=999, user_id=1)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# add_product
# ---------------------------------------------------------------------------

class TestAddProduct:
    def test_appends_product_and_commits(self):
        wl = _make_wishlist(products=[])
        product = _make_product(id=10)
        db = _two_query_db(wl, product)
        db.refresh.side_effect = lambda o: None

        result = add_product(db, wishlist_id=1, product_id=10, user_id=1)

        assert product in wl.products
        db.commit.assert_called_once()
        assert result is wl

    def test_raises_404_when_wishlist_not_found(self):
        from fastapi import HTTPException
        db = _two_query_db(None, _make_product())

        with pytest.raises(HTTPException) as exc:
            add_product(db, wishlist_id=999, product_id=10, user_id=1)
        assert exc.value.status_code == 404
        assert "Wishlist" in exc.value.detail

    def test_raises_404_when_product_not_found(self):
        from fastapi import HTTPException
        wl = _make_wishlist(products=[])
        db = _two_query_db(wl, None)

        with pytest.raises(HTTPException) as exc:
            add_product(db, wishlist_id=1, product_id=999, user_id=1)
        assert exc.value.status_code == 404
        assert "Product" in exc.value.detail

    def test_idempotent_when_already_present(self):
        product = _make_product(id=10)
        wl = _make_wishlist(products=[product])
        db = _two_query_db(wl, product)
        db.refresh.side_effect = lambda o: None

        add_product(db, wishlist_id=1, product_id=10, user_id=1)

        db.commit.assert_not_called()
        assert wl.products.count(product) == 1


# ---------------------------------------------------------------------------
# remove_product
# ---------------------------------------------------------------------------

class TestRemoveProduct:
    def test_removes_product_and_commits(self):
        product = _make_product(id=10)
        wl = _make_wishlist(products=[product])
        db = _two_query_db(wl, product)
        db.refresh.side_effect = lambda o: None

        result = remove_product(db, wishlist_id=1, product_id=10, user_id=1)

        assert product not in wl.products
        db.commit.assert_called_once()
        assert result is wl

    def test_raises_404_when_product_not_in_wishlist(self):
        from fastapi import HTTPException
        product = _make_product(id=10)
        wl = _make_wishlist(products=[])  # empty list
        db = _two_query_db(wl, product)

        with pytest.raises(HTTPException) as exc:
            remove_product(db, wishlist_id=1, product_id=10, user_id=1)
        assert exc.value.status_code == 404

    def test_raises_404_when_wishlist_not_found(self):
        from fastapi import HTTPException
        db = _two_query_db(None, _make_product())

        with pytest.raises(HTTPException) as exc:
            remove_product(db, wishlist_id=999, product_id=10, user_id=1)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TestWishListSchemas:
    def test_create_rejects_empty_name(self):
        with pytest.raises(Exception):
            WishListCreate(name="")

    def test_create_rejects_name_over_100_chars(self):
        with pytest.raises(Exception):
            WishListCreate(name="x" * 101)

    def test_create_accepts_valid_name(self):
        schema = WishListCreate(name="Holiday 2025")
        assert schema.name == "Holiday 2025"

    def test_out_stringifies_datetime(self):
        dt = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        wl = MagicMock(spec=WishList)
        wl.id = 1
        wl.name = "My List"
        wl.created_at = dt
        wl.products = []
        out = WishListOut.model_validate(wl)
        assert "2025-06-01" in out.created_at

    def test_out_embeds_empty_products_list(self):
        wl = MagicMock(spec=WishList)
        wl.id = 1
        wl.name = "Empty"
        wl.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        wl.products = []
        out = WishListOut.model_validate(wl)
        assert out.products == []

    def test_out_accepts_string_created_at(self):
        wl = MagicMock(spec=WishList)
        wl.id = 1
        wl.name = "String date"
        wl.created_at = "2025-01-01T00:00:00+00:00"
        wl.products = []
        out = WishListOut.model_validate(wl)
        assert "2025-01-01" in out.created_at
