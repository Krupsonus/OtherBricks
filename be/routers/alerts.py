"""Price alert endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.price_alert import PriceAlertCreate, PriceAlertOut
from services.price_alert_service import create_alert, delete_alert, get_user_alerts

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[PriceAlertOut])
def list_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all price alerts for the current user with live triggered status."""
    return get_user_alerts(db, current_user.id)


@router.post("", response_model=PriceAlertOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: PriceAlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a price alert. Returns 409 if one already exists for that product."""
    return create_alert(db, current_user.id, payload)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a price alert. Returns 404 if not found or not owned by caller."""
    delete_alert(db, alert_id, current_user.id)
