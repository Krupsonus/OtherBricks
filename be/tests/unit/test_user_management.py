"""Unit tests for user profile update and admin activate/deactivate."""

from unittest.mock import MagicMock, patch

import pytest

from models.user import User, UserRole
from schemas.user import UserUpdateIn
from services.user_service import update_profile
from services.admin_service import set_user_active


def _make_user(id=1, email="user@test.com", role=UserRole.user, is_active=True):
    u = MagicMock(spec=User)
    u.id = id
    u.email = email
    u.first_name = "Jan"
    u.last_name = "Kowalski"
    u.role = role
    u.is_active = is_active
    u.password_hash = "hashed"
    return u


# ---------------------------------------------------------------------------
# update_profile
# ---------------------------------------------------------------------------

class TestUpdateProfile:
    def test_updates_first_name(self):
        user = _make_user()
        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        result = update_profile(db, user, UserUpdateIn(first_name="Anna"))

        assert user.first_name == "Anna"
        db.commit.assert_called_once()
        assert result is user

    def test_updates_last_name(self):
        user = _make_user()
        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        update_profile(db, user, UserUpdateIn(last_name="Nowak"))

        assert user.last_name == "Nowak"

    def test_updates_email_when_not_taken(self):
        user = _make_user()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.refresh.side_effect = lambda o: None

        update_profile(db, user, UserUpdateIn(email="new@test.com"))

        assert user.email == "new@test.com"

    def test_raises_409_when_email_taken(self):
        from fastapi import HTTPException
        user = _make_user()
        other = _make_user(id=2, email="taken@test.com")
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = other

        with pytest.raises(HTTPException) as exc:
            update_profile(db, user, UserUpdateIn(email="taken@test.com"))
        assert exc.value.status_code == 409

    def test_updates_password(self):
        user = _make_user()
        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        with patch("services.user_service.hash_password", return_value="newhash") as mock_hash:
            update_profile(db, user, UserUpdateIn(password="newpassword123"))
            mock_hash.assert_called_once_with("newpassword123")

        assert user.password_hash == "newhash"

    def test_skips_unchanged_email(self):
        user = _make_user(email="same@test.com")
        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        update_profile(db, user, UserUpdateIn(email="same@test.com"))

        # No uniqueness check when email unchanged
        db.query.assert_not_called()

    def test_empty_payload_still_commits(self):
        user = _make_user()
        db = MagicMock()
        db.refresh.side_effect = lambda o: None

        update_profile(db, user, UserUpdateIn())

        db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# set_user_active
# ---------------------------------------------------------------------------

class TestSetUserActive:
    def _db_with_user(self, user):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user
        db.refresh.side_effect = lambda o: None
        return db

    def test_activates_user(self):
        user = _make_user(is_active=False)
        db = self._db_with_user(user)

        result = set_user_active(db, user_id=1, is_active=True)

        assert user.is_active is True
        db.commit.assert_called_once()
        assert result is user

    def test_deactivates_regular_user(self):
        user = _make_user(is_active=True, role=UserRole.user)
        db = self._db_with_user(user)

        set_user_active(db, user_id=1, is_active=False)

        assert user.is_active is False

    def test_raises_404_when_user_not_found(self):
        from fastapi import HTTPException
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            set_user_active(db, user_id=999, is_active=False)
        assert exc.value.status_code == 404

    def test_raises_400_when_deactivating_admin(self):
        from fastapi import HTTPException
        user = _make_user(role=UserRole.admin, is_active=True)
        db = self._db_with_user(user)

        with pytest.raises(HTTPException) as exc:
            set_user_active(db, user_id=1, is_active=False)
        assert exc.value.status_code == 400

    def test_can_activate_admin(self):
        user = _make_user(role=UserRole.admin, is_active=False)
        db = self._db_with_user(user)

        set_user_active(db, user_id=1, is_active=True)

        assert user.is_active is True


# ---------------------------------------------------------------------------
# UserUpdateIn schema
# ---------------------------------------------------------------------------

class TestUserUpdateIn:
    def test_all_fields_optional(self):
        payload = UserUpdateIn()
        assert payload.first_name is None
        assert payload.email is None

    def test_rejects_short_password(self):
        with pytest.raises(Exception):
            UserUpdateIn(password="short")

    def test_rejects_empty_first_name(self):
        with pytest.raises(Exception):
            UserUpdateIn(first_name="")

    def test_accepts_valid_update(self):
        payload = UserUpdateIn(first_name="Anna", last_name="Nowak")
        assert payload.first_name == "Anna"
