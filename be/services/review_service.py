"""Review service — business logic for product reviews."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from models.product import Product
from models.review import Review
from schemas.review import ReviewCreate


def get_product_reviews(db: Session, product_id: int) -> list[Review]:
    """Return all reviews for a product, newest first, with author loaded."""
    return (
        db.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
        .all()
    )


def create_review(db: Session, product_id: int, user_id: int, payload: ReviewCreate) -> Review:
    """Create a review. Raises 404 if product missing, 409 if already reviewed."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this product.",
        )
    db.refresh(review)
    db.refresh(review, ["user"])
    return review


def delete_review(db: Session, review_id: int, user_id: int) -> None:
    """Delete a review. Raises 404 if not found or not owned by user."""
    review = (
        db.query(Review)
        .filter(Review.id == review_id, Review.user_id == user_id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    db.delete(review)
    db.commit()
