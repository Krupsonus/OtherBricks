from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.product import CategoryOut, PriceOfferOut, ProductListResponse, ProductOut
from services.product_service import (
    get_all_categories,
    get_price_offers,
    get_product_by_id,
    get_products,
)

router = APIRouter(tags=["Catalogue"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """Return all product categories."""
    return get_all_categories(db)


@router.get("/products", response_model=ProductListResponse)
def list_products(
    search: str | None = Query(None, description="Search in product name"),
    manufacturer: str | None = Query(None, description="Filter by manufacturer"),
    category_id: int | None = Query(None, description="Filter by category ID"),
    min_price: float | None = Query(None, ge=0, description="Minimum price"),
    max_price: float | None = Query(None, ge=0, description="Maximum price"),
    min_pieces: int | None = Query(None, ge=1, description="Minimum piece count"),
    max_pieces: int | None = Query(None, ge=1, description="Maximum piece count"),
    min_age: int | None = Query(None, ge=0, description="Minimum age rating"),
    limit: int = Query(20, ge=1, le=20, description="Results per page (max 20)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """List products with optional filters and pagination."""
    items, total = get_products(
        db,
        search=search,
        manufacturer=manufacturer,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_pieces=min_pieces,
        max_pieces=max_pieces,
        min_age=min_age,
        limit=limit,
        offset=offset,
    )
    return ProductListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Return a single product by ID."""
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.get("/products/{product_id}/offers", response_model=list[PriceOfferOut])
def list_price_offers(product_id: int, db: Session = Depends(get_db)):
    """Return all external price offers for a product, sorted cheapest first."""
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return get_price_offers(db, product_id)
