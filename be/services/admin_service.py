"""Admin service — product CRUD and admin-only data views."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from models.category import Category
from models.order import Order
from models.product import Product
from models.user import User
from schemas.admin import ProductCreateIn, ProductUpdateIn


def get_all_products(db: Session) -> list[Product]:
    """Return all products with category loaded, newest first."""
    return (
        db.query(Product)
        .options(joinedload(Product.category))
        .order_by(Product.id.desc())
        .all()
    )


def create_product(db: Session, payload: ProductCreateIn) -> Product:
    """Create a new product. Validates category exists if provided."""
    if payload.category_id:
        if not db.query(Category).filter(Category.id == payload.category_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, payload: ProductUpdateIn) -> Product:
    """Update a product. Only sets fields explicitly provided (non-None)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    """Delete a product. Raises 404 if not found."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    db.delete(product)
    db.commit()


def get_all_orders(db: Session) -> list[Order]:
    """Return all orders across all users, newest first."""
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .order_by(Order.created_at.desc())
        .all()
    )


def get_all_users(db: Session) -> list[User]:
    """Return all registered users, newest first."""
    return db.query(User).order_by(User.id.desc()).all()
