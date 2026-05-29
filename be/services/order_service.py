"""Order service — business logic for cart checkout and order history."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from models.order import Order, OrderItem, OrderStatus
from models.product import Product
from schemas.order import CartItemIn, OrderCreateIn


def _mock_stripe_charge(amount: float, payment_method: str) -> str:
    """Simulate a Stripe payment. Returns a fake payment intent ID."""
    return f"pi_mock_{int(amount * 100):010d}"


def create_order(db: Session, user_id: int, payload: OrderCreateIn) -> Order:
    """Validate cart, snapshot prices, mock Stripe, persist order."""
    product_ids = [item.product_id for item in payload.items]
    products = {
        p.id: p
        for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
    }

    # Validate all products exist and have sufficient stock
    for item in payload.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Product {item.product_id} not found.",
            )
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Insufficient stock for '{product.name}' "
                       f"(available: {product.stock_quantity}).",
            )

    total = sum(
        float(products[item.product_id].base_price) * item.quantity
        for item in payload.items
    )

    _mock_stripe_charge(total, payload.payment_method)

    order = Order(
        user_id=user_id,
        status=OrderStatus.paid,  # mock payment always succeeds
        total_amount=round(total, 2),
        shipping_address=payload.shipping_address,
        payment_method=payload.payment_method,
    )
    db.add(order)
    db.flush()  # get order.id before creating items

    order_items = [
        OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=float(products[item.product_id].base_price),
        )
        for item in payload.items
    ]
    db.add_all(order_items)

    # Decrement stock
    for item in payload.items:
        products[item.product_id].stock_quantity -= item.quantity

    db.commit()
    db.refresh(order)
    return order


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    """Return all orders for a user, newest first, with items loaded."""
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order(db: Session, order_id: int, user_id: int) -> Order | None:
    """Return a single order if it belongs to the requesting user."""
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id, Order.user_id == user_id)
        .first()
    )
