"""Wishlist endpoints — manage user wishlists and their products."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.wish_list import WishListCreate, WishListOut
from services.wish_list_service import (
    add_product,
    create_wishlist,
    delete_wishlist,
    get_user_wishlists,
    remove_product,
)

router = APIRouter(prefix="/wishlists", tags=["Wishlists"])


@router.get("", response_model=list[WishListOut])
def list_wishlists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all wishlists belonging to the current user."""
    return get_user_wishlists(db, current_user.id)


@router.post("", response_model=WishListOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: WishListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new wishlist for the current user."""
    return create_wishlist(db, current_user.id, payload)


@router.delete("/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    wishlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a wishlist. Returns 404 if not found or not owned by caller."""
    delete_wishlist(db, wishlist_id, current_user.id)


@router.post("/{wishlist_id}/products/{product_id}", response_model=WishListOut)
def add_product_to_wishlist(
    wishlist_id: int,
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a product to a wishlist. Idempotent."""
    return add_product(db, wishlist_id, product_id, current_user.id)


@router.delete("/{wishlist_id}/products/{product_id}", response_model=WishListOut)
def remove_product_from_wishlist(
    wishlist_id: int,
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a product from a wishlist. Returns 404 if not present."""
    return remove_product(db, wishlist_id, product_id, current_user.id)
