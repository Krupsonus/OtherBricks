from sqlalchemy.orm import Session, joinedload

from models.category import Category
from models.product import Product

MAX_PAGE_SIZE = 20


def get_products(
    db: Session,
    *,
    search: str | None = None,
    manufacturer: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_pieces: int | None = None,
    max_pieces: int | None = None,
    min_age: int | None = None,
    limit: int = MAX_PAGE_SIZE,
    offset: int = 0,
) -> tuple[list[Product], int]:
    """Return a filtered, paginated list of products and the total count.

    Limit is capped at MAX_PAGE_SIZE (20) per NF03.
    """
    limit = min(limit, MAX_PAGE_SIZE)
    query = db.query(Product).options(joinedload(Product.category))

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if manufacturer:
        query = query.filter(Product.manufacturer.ilike(f"%{manufacturer}%"))
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.base_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.base_price <= max_price)
    if min_pieces is not None:
        query = query.filter(Product.piece_count >= min_pieces)
    if max_pieces is not None:
        query = query.filter(Product.piece_count <= max_pieces)
    if min_age is not None:
        query = query.filter(Product.min_age >= min_age)

    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return items, total


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    """Return a single product with its category loaded, or None if not found."""
    return (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id == product_id)
        .first()
    )


def get_all_categories(db: Session) -> list[Category]:
    """Return all categories ordered by name."""
    return db.query(Category).order_by(Category.name).all()
