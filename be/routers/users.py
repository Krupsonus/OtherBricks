"""User profile endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.user import UserOut, UserUpdateIn
from services.user_service import update_profile

router = APIRouter(prefix="/users", tags=["Users"])


@router.put("/me", response_model=UserOut)
def update_me(
    payload: UserUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's own profile (partial update)."""
    return update_profile(db, current_user, payload)
