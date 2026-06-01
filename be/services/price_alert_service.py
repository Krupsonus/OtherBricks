"""Price alert service — business logic for user price thresholds."""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from models.price_alert import PriceAlert
from models.price_offer import PriceOffer
from models.product import Product
from schemas.price_alert import PriceAlertCreate, PriceAlertOut


def _enrich(alert: PriceAlert, best_price: Decimal | None) -> dict:
    """Build a PriceAlertOut-compatible dict from an alert and its best offer price."""
    best = float(best_price) if best_price is not None else None
    return {
        "id": alert.id,
        "product_id": alert.product_id,
        "product_name": alert.product.name,
        "target_price": float(alert.target_price),
        "best_offer_price": best,
        "is_triggered": best is not None and best <= float(alert.target_price),
        "created_at": alert.created_at,
    }


def get_user_alerts(db: Session, user_id: int) -> list[PriceAlertOut]:
    """Return all alerts for a user enriched with current best offer price."""
    alerts = (
        db.query(PriceAlert)
        .options(joinedload(PriceAlert.product))
        .filter(PriceAlert.user_id == user_id)
        .order_by(PriceAlert.created_at.desc())
        .all()
    )
    if not alerts:
        return []

    product_ids = [a.product_id for a in alerts]
    min_prices: dict[int, Decimal] = dict(
        db.query(PriceOffer.product_id, func.min(PriceOffer.price))
        .filter(PriceOffer.product_id.in_(product_ids))
        .group_by(PriceOffer.product_id)
        .all()
    )

    return [PriceAlertOut(**_enrich(a, min_prices.get(a.product_id))) for a in alerts]


def create_alert(db: Session, user_id: int, payload: PriceAlertCreate) -> PriceAlertOut:
    """Create a price alert. Raises 404 if product missing, 409 if alert already exists."""
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    alert = PriceAlert(
        user_id=user_id,
        product_id=payload.product_id,
        target_price=payload.target_price,
    )
    db.add(alert)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an alert for this product.",
        )
    db.refresh(alert)
    # load product relationship for name
    alert.product = product

    best_price = (
        db.query(func.min(PriceOffer.price))
        .filter(PriceOffer.product_id == alert.product_id)
        .scalar()
    )
    return PriceAlertOut(**_enrich(alert, best_price))


def delete_alert(db: Session, alert_id: int, user_id: int) -> None:
    """Delete an alert. Raises 404 if not found or not owned by caller."""
    alert = (
        db.query(PriceAlert)
        .filter(PriceAlert.id == alert_id, PriceAlert.user_id == user_id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    db.delete(alert)
    db.commit()
