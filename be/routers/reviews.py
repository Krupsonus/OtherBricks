"""Review endpoints — read and submit product reviews."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.review import ReviewCreate, ReviewOut
from services.review_service import create_review, delete_review, get_product_reviews

router = APIRouter(tags=["Reviews"])


@router.get("/products/{product_id}/reviews", response_model=list[ReviewOut])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    """Return all reviews for a product, newest first. Public endpoint."""
    return get_product_reviews(db, product_id)


@router.post(
    "/products/{product_id}/reviews",
    response_model=ReviewOut,
    status_code=status.HTTP_201_CREATED,
)
def submit_review(
    product_id: int,
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a review for a product. Returns 409 if user already reviewed it."""
    return create_review(db, product_id, current_user.id, payload)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete own review. Returns 404 if not found or not owned by caller."""
    delete_review(db, review_id, current_user.id)
