"""Unit tests for the User model and UserRole enum."""

import pytest
from unittest.mock import MagicMock, patch
from passlib.context import CryptContext

from models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestUserRole:
    def test_role_values(self):
        assert UserRole.user == "user"
        assert UserRole.admin == "admin"

    def test_role_is_str(self):
        assert isinstance(UserRole.user, str)
        assert isinstance(UserRole.admin, str)

    def test_role_from_string(self):
        assert UserRole("user") == UserRole.user
        assert UserRole("admin") == UserRole.admin

    def test_invalid_role_raises(self):
        with pytest.raises(ValueError):
            UserRole("superuser")


class TestUserModel:
    def test_user_tablename(self):
        assert User.__tablename__ == "users"

    def test_user_has_required_columns(self):
        columns = {col.name for col in User.__table__.columns}
        required = {"id", "email", "password_hash", "first_name", "last_name",
                    "role", "is_active", "created_at"}
        assert required.issubset(columns)

    def test_user_email_is_unique(self):
        email_col = User.__table__.columns["email"]
        assert email_col.unique

    def test_user_email_is_indexed(self):
        indexed_cols = {idx.columns.keys()[0] for idx in User.__table__.indexes
                        if len(list(idx.columns)) == 1}
        assert "email" in indexed_cols

    def test_user_is_active_default(self):
        is_active_col = User.__table__.columns["is_active"]
        assert is_active_col.default.arg is True

    def test_user_role_default(self):
        role_col = User.__table__.columns["role"]
        assert role_col.default.arg == UserRole.user

    def test_password_hash_not_stored_plain(self):
        """Verify that a bcrypt hash is produced and differs from the original."""
        plain = "secret123"
        hashed = pwd_context.hash(plain)
        assert hashed != plain
        assert pwd_context.verify(plain, hashed)

    def test_password_verification_wrong_password(self):
        plain = "correct"
        hashed = pwd_context.hash(plain)
        assert not pwd_context.verify("wrong", hashed)

    def test_user_instantiation(self):
        user = User(
            email="test@example.com",
            password_hash=pwd_context.hash("pass"),
            first_name="Jan",
            last_name="Kowalski",
            role=UserRole.user,
            is_active=True,
        )
        assert user.email == "test@example.com"
        assert user.first_name == "Jan"
        assert user.last_name == "Kowalski"
        assert user.role == UserRole.user
        assert user.is_active is True

    def test_admin_instantiation(self):
        admin = User(
            email="admin@example.com",
            password_hash=pwd_context.hash("adminpass"),
            first_name="Admin",
            last_name="OtherBricks",
            role=UserRole.admin,
            is_active=True,
        )
        assert admin.role == UserRole.admin


class TestSeedScript:
    """Tests for the seed.py logic (isolated — no real DB)."""

    def test_seed_skips_if_admin_exists(self):
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = MagicMock()  # admin already exists

        import seed
        seed.seed(mock_db)

        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    def test_seed_creates_admin_if_not_exists(self):
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # admin does not exist

        import seed
        seed.seed(mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_seed_admin_has_correct_role(self):
        added_objects = []
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.add.side_effect = lambda obj: added_objects.append(obj)

        import seed
        seed.seed(mock_db)

        assert len(added_objects) == 1
        admin = added_objects[0]
        assert admin.email == "admin@otherbricks.com"
        assert admin.role == UserRole.admin
        assert admin.is_active is True
