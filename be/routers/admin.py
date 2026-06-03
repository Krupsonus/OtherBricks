"""Admin-only endpoints for product management and data overview."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_admin
from models.notification import Notification
from models.user import User
from schemas.admin import AdminOrderOut, ProductCreateIn, ProductUpdateIn, UserAdminOut
from schemas.notification import NotificationOut
from schemas.product import ProductOut
from services.admin_service import (
    create_product,
    delete_product,
    get_all_orders,
    get_all_products,
    get_all_users,
    set_user_active,
    update_product,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/products", response_model=list[ProductOut])
def list_products(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all products (admin view includes updated_at)."""
    return get_all_products(db)


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def add_product(
    payload: ProductCreateIn,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new product."""
    return create_product(db, payload)


@router.put("/products/{product_id}", response_model=ProductOut)
def edit_product(
    product_id: int,
    payload: ProductUpdateIn,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update an existing product. Returns 404 if not found."""
    return update_product(db, product_id, payload)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product(
    product_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a product. Returns 404 if not found."""
    delete_product(db, product_id)


@router.get("/orders", response_model=list[AdminOrderOut])
def list_orders(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all orders across all users, newest first."""
    return get_all_orders(db)


@router.get("/users", response_model=list[UserAdminOut])
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all registered users."""
    return get_all_users(db)


@router.put("/users/{user_id}/activate", response_model=UserAdminOut)
def activate_user(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Activate a user account. Returns 404 if not found."""
    return set_user_active(db, user_id, True)


@router.post("/aggregate", status_code=status.HTTP_202_ACCEPTED)
def trigger_aggregation(
    _: User = Depends(require_admin),
):
    """Queue the price aggregation Celery task. Returns the task ID."""
    from tasks.price_aggregator import aggregate_prices
    task = aggregate_prices.delay()
    return {"task_id": task.id, "status": "queued"}


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List the 100 most recent price alert notifications."""
    return (
        db.query(Notification)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )


@router.put("/users/{user_id}/deactivate", response_model=UserAdminOut)
def deactivate_user(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Deactivate a user account. Returns 404 if not found, 400 if target is admin."""
    return set_user_active(db, user_id, False)
