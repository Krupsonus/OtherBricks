"""User profile management service."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User
from schemas.user import UserUpdateIn
from services.auth_service import hash_password


def update_profile(db: Session, user: User, payload: UserUpdateIn) -> User:
    """Update the authenticated user's own profile. Raises 409 if new email is taken."""
    if payload.email is not None and payload.email != user.email:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "password":
            user.password_hash = hash_password(value)
        else:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
