"""Unit tests for review service and schemas."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from models.review import Review
from models.user import User
from models.product import Product
from schemas.review import ReviewCreate, ReviewOut
from services.review_service import create_review, delete_review, get_product_reviews


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(id=1, first_name="Jan", last_name="Kowalski"):
    u = MagicMock(spec=User)
    u.id = id
    u.first_name = first_name
    u.last_name = last_name
    return u


def _make_review(id=1, user_id=1, product_id=5, rating=4, comment="Good"):
    r = MagicMock(spec=Review)
    r.id = id
    r.user_id = user_id
    r.product_id = product_id
    r.rating = rating
    r.comment = comment
    r.created_at = datetime(2025, 6, 1, tzinfo=timezone.utc)
    r.user = _make_user(id=user_id)
    r.author_name = f"{r.user.first_name} {r.user.last_name}"
    return r


def _make_product(id=5):
    p = MagicMock(spec=Product)
    p.id = id
    return p


def _query_db(first_return, all_return=None):
    db = MagicMock()
    q = db.query.return_value
    q.options.return_value = q
    q.filter.return_value = q
    q.order_by.return_value = q
    q.first.return_value = first_return
    q.all.return_value = all_return if all_return is not None else (
        [first_return] if first_return else []
    )
    return db


def _two_query_db(first_product, first_review):
    """First query returns product, second returns review."""
    db = MagicMock()
    product_q = MagicMock()
    product_q.filter.return_value = product_q
    product_q.first.return_value = first_product

    review_q = MagicMock()
    review_q.filter.return_value = review_q
    review_q.first.return_value = first_review

    db.query.side_effect = [product_q, review_q]
    return db


# ---------------------------------------------------------------------------
# get_product_reviews
# ---------------------------------------------------------------------------

class TestGetProductReviews:
    def test_returns_reviews(self):
        r = _make_review()
        db = _query_db(r, all_return=[r])
        result = get_product_reviews(db, product_id=5)
        assert result == [r]

    def test_returns_empty_when_none(self):
        db = _query_db(None, all_return=[])
        result = get_product_reviews(db, product_id=99)
        assert result == []


# ---------------------------------------------------------------------------
# create_review
# ---------------------------------------------------------------------------

class TestCreateReview:
    def _payload(self, rating=4, comment="Nice"):
        return ReviewCreate(rating=rating, comment=comment)

    def test_raises_404_when_product_not_found(self):
        from fastapi import HTTPException
        db = _query_db(None)
        with pytest.raises(HTTPException) as exc:
            create_review(db, product_id=999, user_id=1, payload=self._payload())
        assert exc.value.status_code == 404

    def test_commits_and_returns_review(self):
        product = _make_product()
        review = _make_review()
        db = _query_db(product)
        db.refresh.side_effect = lambda *args: None

        with patch("services.review_service.Review", return_value=review):
            result = create_review(db, product_id=5, user_id=1, payload=self._payload())

        db.add.assert_called_once_with(review)
        db.commit.assert_called_once()
        assert result is review

    def test_raises_409_on_duplicate(self):
        from fastapi import HTTPException
        from sqlalchemy.exc import IntegrityError

        product = _make_product()
        db = _query_db(product)
        db.commit.side_effect = IntegrityError("", {}, Exception())

        with pytest.raises(HTTPException) as exc:
            create_review(db, product_id=5, user_id=1, payload=self._payload())
        assert exc.value.status_code == 409
        db.rollback.assert_called_once()

    def test_stores_correct_rating(self):
        product = _make_product()
        db = _query_db(product)
        db.refresh.side_effect = lambda *args: None
        captured = {}

        def capture(**kwargs):
            captured.update(kwargs)
            return _make_review(**{k: v for k, v in kwargs.items()
                                   if k in ("id", "user_id", "product_id", "rating", "comment")})

        with patch("services.review_service.Review", side_effect=capture):
            create_review(db, product_id=5, user_id=1, payload=ReviewCreate(rating=2))

        assert captured["rating"] == 2

    def test_stores_none_comment_when_omitted(self):
        product = _make_product()
        db = _query_db(product)
        db.refresh.side_effect = lambda *args: None
        captured = {}

        def capture(**kwargs):
            captured.update(kwargs)
            return _make_review()

        with patch("services.review_service.Review", side_effect=capture):
            create_review(db, product_id=5, user_id=1, payload=ReviewCreate(rating=3))

        assert captured.get("comment") is None


# ---------------------------------------------------------------------------
# delete_review
# ---------------------------------------------------------------------------

class TestDeleteReview:
    def test_deletes_when_found(self):
        review = _make_review()
        db = _query_db(review)

        delete_review(db, review_id=1, user_id=1)

        db.delete.assert_called_once_with(review)
        db.commit.assert_called_once()

    def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        db = _query_db(None)

        with pytest.raises(HTTPException) as exc:
            delete_review(db, review_id=999, user_id=1)
        assert exc.value.status_code == 404

    def test_raises_404_when_not_owner(self):
        from fastapi import HTTPException
        db = _query_db(None)  # filter by (id, user_id) returns nothing

        with pytest.raises(HTTPException) as exc:
            delete_review(db, review_id=1, user_id=99)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TestReviewSchemas:
    def test_rating_must_be_at_least_1(self):
        with pytest.raises(Exception):
            ReviewCreate(rating=0)

    def test_rating_must_be_at_most_5(self):
        with pytest.raises(Exception):
            ReviewCreate(rating=6)

    def test_valid_rating_accepted(self):
        r = ReviewCreate(rating=3)
        assert r.rating == 3

    def test_comment_optional(self):
        r = ReviewCreate(rating=5)
        assert r.comment is None

    def test_out_stringifies_datetime(self):
        review = _make_review()
        out = ReviewOut.model_validate(review)
        assert "2025-06-01" in out.created_at

    def test_out_includes_author_name(self):
        review = _make_review()
        out = ReviewOut.model_validate(review)
        assert out.author_name == "Jan Kowalski"

    def test_out_accepts_string_created_at(self):
        review = _make_review()
        review.created_at = "2025-06-01T00:00:00+00:00"
        out = ReviewOut.model_validate(review)
        assert "2025-06-01" in out.created_at
