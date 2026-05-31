"""Unit tests for auth_service — all DB calls are mocked."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from jose import jwt

from config import settings
from models.user import User, UserRole
from services.auth_service import (
    authenticate_user,
    create_access_token,
    decode_token,
    get_user_by_email,
    hash_password,
    register_user,
    verify_password,
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_differs_from_plain(self):
        hashed = hash_password("mysecret")
        assert hashed != "mysecret"

    def test_hash_starts_with_bcrypt_prefix(self):
        assert hash_password("test").startswith("$2")

    def test_verify_correct_password(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        # bcrypt uses a random salt each time
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


# ---------------------------------------------------------------------------
# JWT token creation & decoding
# ---------------------------------------------------------------------------

class TestTokens:
    def test_create_token_returns_string(self):
        token = create_access_token({"sub": "user@example.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_sub(self):
        token = create_access_token({"sub": "user@example.com"})
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "user@example.com"

    def test_token_contains_exp(self):
        token = create_access_token({"sub": "u@x.com"})
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert "exp" in payload

    def test_decode_valid_token(self):
        token = create_access_token({"sub": "a@b.com"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "a@b.com"

    def test_decode_invalid_token_returns_none(self):
        assert decode_token("not.a.real.token") is None

    def test_decode_tampered_token_returns_none(self):
        token = create_access_token({"sub": "a@b.com"})
        tampered = token[:-5] + "XXXXX"
        assert decode_token(tampered) is None

    def test_decode_expired_token_returns_none(self):
        expired_payload = {
            "sub": "a@b.com",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        }
        token = jwt.encode(expired_payload, settings.secret_key, algorithm=settings.algorithm)
        assert decode_token(token) is None

    def test_token_role_included(self):
        token = create_access_token({"sub": "a@b.com", "role": "admin"})
        payload = decode_token(token)
        assert payload["role"] == "admin"


# ---------------------------------------------------------------------------
# Database-level functions (DB mocked)
# ---------------------------------------------------------------------------

class TestGetUserByEmail:
    def _make_db(self, result):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = result
        return db

    def test_returns_user_when_found(self):
        user = User(email="a@b.com")
        db = self._make_db(user)
        assert get_user_by_email(db, "a@b.com") is user

    def test_returns_none_when_not_found(self):
        db = self._make_db(None)
        assert get_user_by_email(db, "missing@b.com") is None


class TestRegisterUser:
    def test_adds_and_commits(self):
        db = MagicMock()
        result = register_user(db, "new@b.com", "pass123", "Jan", "Kowalski")
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    def test_password_is_hashed(self):
        added = []
        db = MagicMock()
        db.add.side_effect = lambda u: added.append(u)
        register_user(db, "x@b.com", "plain", "A", "B")
        assert added[0].password_hash != "plain"
        assert added[0].password_hash.startswith("$2")

    def test_email_stored_correctly(self):
        added = []
        db = MagicMock()
        db.add.side_effect = lambda u: added.append(u)
        register_user(db, "test@example.com", "pass", "Tom", "Smith")
        assert added[0].email == "test@example.com"
        assert added[0].first_name == "Tom"
        assert added[0].last_name == "Smith"


class TestUserSchemas:
    def test_login_request_validates_email(self):
        from schemas.user import LoginRequest
        lr = LoginRequest(email="user@example.com", password="secret")
        assert lr.email == "user@example.com"

    def test_token_default_type_is_bearer(self):
        from schemas.user import Token
        t = Token(access_token="abc123")
        assert t.token_type == "bearer"

    def test_user_create_stores_fields(self):
        from schemas.user import UserCreate
        uc = UserCreate(email="a@b.com", password="pass", first_name="Jan", last_name="Kowalski")
        assert uc.first_name == "Jan"


class TestAuthenticateUser:
    def _user_with_hash(self, password: str) -> User:
        u = User()
        u.email = "a@b.com"
        u.password_hash = hash_password(password)
        u.is_active = True
        return u

    def test_returns_user_on_valid_credentials(self):
        user = self._user_with_hash("secret")
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user
        result = authenticate_user(db, "a@b.com", "secret")
        assert result is user

    def test_returns_none_on_wrong_password(self):
        user = self._user_with_hash("correct")
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user
        assert authenticate_user(db, "a@b.com", "wrong") is None

    def test_returns_none_when_user_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        assert authenticate_user(db, "missing@b.com", "any") is None
