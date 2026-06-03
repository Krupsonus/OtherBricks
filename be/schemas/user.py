from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.user import UserRole


class UserCreate(BaseModel):
    """Payload for registering a new user account."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserUpdateIn(BaseModel):
    """Partial update of the authenticated user's own profile."""
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)


class UserOut(BaseModel):
    """Public representation of a user account (no password hash)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    """Credentials for obtaining a JWT access token."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT access token returned after successful login."""
    access_token: str
    token_type: str = "bearer"
