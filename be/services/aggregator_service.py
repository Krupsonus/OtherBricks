"""Price aggregation business logic — kept separate from the Celery task for testability."""

import random
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from models.notification import Notification
from models.price_alert import PriceAlert
from models.price_offer import PriceOffer
from models.product import Product

# Three simulated external aggregator bots
_MOCK_SHOPS = [
    ("BrickBot Alpha", "https://brickbot-alpha.example.com"),
    ("BrickBot Beta", "https://brickbot-beta.example.com"),
    ("BrickBot Gamma", "https://brickbot-gamma.example.com"),
]


def generate_mock_prices(base_price: float) -> list[tuple[str, str, float]]:
    """Return (shop_name, shop_url, price) for each mock shop.

    Prices fluctuate ±20 % around the product's base price.
    """
    results = []
    for shop_name, shop_url in _MOCK_SHOPS:
        multiplier = random.uniform(0.80, 1.20)
        price = round(float(base_price) * multiplier, 2)
        results.append((shop_name, shop_url, price))
    return results


def upsert_price_offer(
    db: Session, product_id: int, shop_name: str, shop_url: str, price: float
) -> PriceOffer:
    """Update existing offer for (product_id, shop_name) or create a new one."""
    offer = (
        db.query(PriceOffer)
        .filter(PriceOffer.product_id == product_id, PriceOffer.shop_name == shop_name)
        .first()
    )
    if offer:
        offer.price = price
        offer.shop_url = shop_url
    else:
        offer = PriceOffer(product_id=product_id, shop_name=shop_name, shop_url=shop_url, price=price)
        db.add(offer)
    return offer


def check_and_notify_alerts(db: Session, updated_product_ids: list[int]) -> list[Notification]:
    """Create Notification records for any triggered price alerts."""
    if not updated_product_ids:
        return []

    alerts = (
        db.query(PriceAlert)
        .options(joinedload(PriceAlert.product), joinedload(PriceAlert.user))
        .filter(PriceAlert.product_id.in_(updated_product_ids))
        .all()
    )

    # Compute min price per product in a single query
    from sqlalchemy import func
    min_prices = dict(
        db.query(PriceOffer.product_id, func.min(PriceOffer.price))
        .filter(PriceOffer.product_id.in_(updated_product_ids))
        .group_by(PriceOffer.product_id)
        .all()
    )

    notifications = []
    for alert in alerts:
        best = min_prices.get(alert.product_id)
        if best is not None and float(best) <= float(alert.target_price):
            msg = (
                f"Price alert triggered for \"{alert.product.name}\": "
                f"best price is now ${float(best):.2f} "
                f"(your target: ${float(alert.target_price):.2f})."
            )
            notif = Notification(
                user_id=alert.user_id,
                type="price_alert",
                message=msg,
                is_sent=False,
            )
            db.add(notif)
            notifications.append(notif)

    return notifications


def run_aggregation(db: Session) -> dict:
    """Fetch all products, generate mock prices, check alerts. Returns a stats dict."""
    products = db.query(Product).all()

    updated_ids = []
    offers_updated = 0

    for product in products:
        mock_prices = generate_mock_prices(float(product.base_price))
        for shop_name, shop_url, price in mock_prices:
            upsert_price_offer(db, product.id, shop_name, shop_url, price)
            offers_updated += 1
        updated_ids.append(product.id)

    db.flush()

    notifications = check_and_notify_alerts(db, updated_ids)
    db.commit()

    return {
        "products_processed": len(products),
        "offers_updated": offers_updated,
        "alerts_triggered": len(notifications),
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }
