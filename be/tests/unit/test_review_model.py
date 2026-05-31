"""Unit tests for Review model."""

from models.review import Review


class TestReviewModel:
    def test_tablename(self):
        assert Review.__tablename__ == "reviews"

    def test_required_columns(self):
        cols = {c.name for c in Review.__table__.columns}
        assert {"id", "user_id", "product_id", "rating", "created_at"}.issubset(cols)

    def test_comment_is_nullable(self):
        assert Review.__table__.columns["comment"].nullable

    def test_rating_not_nullable(self):
        assert not Review.__table__.columns["rating"].nullable

    def test_user_id_not_nullable(self):
        assert not Review.__table__.columns["user_id"].nullable

    def test_product_id_not_nullable(self):
        assert not Review.__table__.columns["product_id"].nullable

    def test_user_id_indexed(self):
        indexed = {list(i.columns)[0].name for i in Review.__table__.indexes}
        assert "user_id" in indexed

    def test_product_id_indexed(self):
        indexed = {list(i.columns)[0].name for i in Review.__table__.indexes}
        assert "product_id" in indexed

    def test_user_fk_references_users(self):
        fk = list(Review.__table__.columns["user_id"].foreign_keys)[0]
        assert "users" in fk.target_fullname

    def test_product_fk_references_products(self):
        fk = list(Review.__table__.columns["product_id"].foreign_keys)[0]
        assert "products" in fk.target_fullname

    def test_user_fk_cascade_delete(self):
        fk = list(Review.__table__.columns["user_id"].foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_product_fk_cascade_delete(self):
        fk = list(Review.__table__.columns["product_id"].foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_unique_constraint_on_user_product(self):
        constraint_names = {c.name for c in Review.__table__.constraints}
        assert "uq_review_user_product" in constraint_names

    def test_instantiation(self):
        r = Review(user_id=1, product_id=5, rating=4, comment="Great set!")
        assert r.user_id == 1
        assert r.product_id == 5
        assert r.rating == 4
        assert r.comment == "Great set!"

    def test_instantiation_without_comment(self):
        r = Review(user_id=2, product_id=3, rating=5)
        assert r.comment is None
