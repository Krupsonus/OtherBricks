"""Wishlist service — business logic for wishlist CRUD and product management."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.product import Product
from models.wish_list import WishList
from schemas.wish_list import WishListCreate


def _get_owned_wishlist(db: Session, wishlist_id: int, user_id: int) -> WishList:
    """Return a wishlist if it exists and belongs to the user, else raise 404."""
    wl = (
        db.query(WishList)
        .filter(WishList.id == wishlist_id, WishList.user_id == user_id)
        .first()
    )
    if not wl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found.")
    return wl


def get_user_wishlists(db: Session, user_id: int) -> list[WishList]:
    """Return all wishlists for a user, newest first."""
    return (
        db.query(WishList)
        .filter(WishList.user_id == user_id)
        .order_by(WishList.created_at.desc())
        .all()
    )


def create_wishlist(db: Session, user_id: int, payload: WishListCreate) -> WishList:
    """Create a new named wishlist for the user."""
    wl = WishList(user_id=user_id, name=payload.name)
    db.add(wl)
    db.commit()
    db.refresh(wl)
    return wl


def delete_wishlist(db: Session, wishlist_id: int, user_id: int) -> None:
    """Delete a wishlist. Raises 404 if not found or not owned by user."""
    wl = _get_owned_wishlist(db, wishlist_id, user_id)
    db.delete(wl)
    db.commit()


def add_product(db: Session, wishlist_id: int, product_id: int, user_id: int) -> WishList:
    """Add a product to a wishlist. Idempotent — no error if already present."""
    wl = _get_owned_wishlist(db, wishlist_id, user_id)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    if product not in wl.products:
        wl.products.append(product)
        db.commit()
        db.refresh(wl)
    return wl


def remove_product(db: Session, wishlist_id: int, product_id: int, user_id: int) -> WishList:
    """Remove a product from a wishlist. Raises 404 if not in list."""
    wl = _get_owned_wishlist(db, wishlist_id, user_id)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product not in wl.products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not in wishlist."
        )
    wl.products.remove(product)
    db.commit()
    db.refresh(wl)
    return wl
