"""Unit tests for WishList model and wish_list_products association table."""

from models.wish_list import WishList, wish_list_products


class TestWishListModel:
    def test_tablename(self):
        assert WishList.__tablename__ == "wish_lists"

    def test_required_columns(self):
        cols = {c.name for c in WishList.__table__.columns}
        assert {"id", "user_id", "name", "created_at"}.issubset(cols)

    def test_user_id_not_nullable(self):
        assert not WishList.__table__.columns["user_id"].nullable

    def test_name_not_nullable(self):
        assert not WishList.__table__.columns["name"].nullable

    def test_name_max_length(self):
        assert WishList.__table__.columns["name"].type.length == 100

    def test_user_id_indexed(self):
        indexed = {list(i.columns)[0].name for i in WishList.__table__.indexes}
        assert "user_id" in indexed

    def test_user_fk_references_users(self):
        fk = list(WishList.__table__.columns["user_id"].foreign_keys)[0]
        assert "users" in fk.target_fullname

    def test_user_fk_cascade_delete(self):
        fk = list(WishList.__table__.columns["user_id"].foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_instantiation(self):
        wl = WishList(user_id=1, name="Favourites")
        assert wl.user_id == 1
        assert wl.name == "Favourites"


class TestWishListProductsTable:
    def test_tablename(self):
        assert wish_list_products.name == "wish_list_products"

    def test_columns(self):
        cols = {c.name for c in wish_list_products.columns}
        assert cols == {"wish_list_id", "product_id"}

    def test_both_columns_are_primary_keys(self):
        pk_cols = {c.name for c in wish_list_products.primary_key}
        assert pk_cols == {"wish_list_id", "product_id"}

    def test_wish_list_id_fk_references_wish_lists(self):
        col = wish_list_products.columns["wish_list_id"]
        fk = list(col.foreign_keys)[0]
        assert "wish_lists" in fk.target_fullname

    def test_product_id_fk_references_products(self):
        col = wish_list_products.columns["product_id"]
        fk = list(col.foreign_keys)[0]
        assert "products" in fk.target_fullname

    def test_wish_list_id_cascade_delete(self):
        col = wish_list_products.columns["wish_list_id"]
        fk = list(col.foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_product_id_cascade_delete(self):
        col = wish_list_products.columns["product_id"]
        fk = list(col.foreign_keys)[0]
        assert fk.ondelete == "CASCADE"
