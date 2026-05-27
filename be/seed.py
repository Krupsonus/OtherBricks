"""Database seed script.

Creates initial data required for the application to function:
- Default admin account (admin@otherbricks.com / admin123)
- Sample categories and products for development and testing

Run once after the database tables have been created:
    docker compose exec backend python seed.py
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
import models  # noqa: F401

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_admin(db: Session) -> None:
    from models.user import User, UserRole

    if db.query(User).filter(User.email == "admin@otherbricks.com").first():
        print("Admin already exists — skipping.")
        return

    admin = User(
        email="admin@otherbricks.com",
        password_hash=pwd_context.hash("admin123"),
        first_name="Admin",
        last_name="OtherBricks",
        role=UserRole.admin,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print("Seed complete: admin@otherbricks.com created.")


def seed_catalog(db: Session) -> None:
    from models.category import Category
    from models.product import Product

    if db.query(Category).first():
        print("Catalog already seeded — skipping.")
        return

    categories = [
        Category(name="Military", description="Tanks, planes and historical military sets"),
        Category(name="Architecture", description="Famous buildings and city landmarks"),
        Category(name="Vehicles", description="Cars, trucks and racing vehicles"),
        Category(name="Space", description="Rockets, space stations and sci-fi builds"),
    ]
    db.add_all(categories)
    db.flush()

    military = next(c for c in categories if c.name == "Military")
    arch = next(c for c in categories if c.name == "Architecture")
    vehicles = next(c for c in categories if c.name == "Vehicles")
    space = next(c for c in categories if c.name == "Space")

    products = [
        Product(name="COBI Panzer IV", manufacturer="Cobi", piece_count=500,
                min_age=8, base_price=89.99, stock_quantity=20,
                category_id=military.id,
                description="Detailed 1:35 scale WWII Panzer IV tank model."),
        Product(name="COBI Spitfire Mk.I", manufacturer="Cobi", piece_count=370,
                min_age=8, base_price=69.99, stock_quantity=15,
                category_id=military.id,
                description="Iconic British WWII fighter plane."),
        Product(name="CaDA Eiffel Tower", manufacturer="CaDA", piece_count=1050,
                min_age=12, base_price=129.99, stock_quantity=8,
                category_id=arch.id,
                description="Detailed micro-scale Eiffel Tower."),
        Product(name="Mega Construx Porsche 911", manufacturer="Mega Construx",
                piece_count=1288, min_age=14, base_price=199.99, stock_quantity=5,
                category_id=vehicles.id,
                description="Highly detailed Porsche 911 with opening hood."),
        Product(name="CaDA Space Shuttle", manufacturer="CaDA", piece_count=780,
                min_age=10, base_price=99.99, stock_quantity=12,
                category_id=space.id,
                description="NASA-inspired space shuttle with launch platform."),
        Product(name="COBI Titanic", manufacturer="Cobi", piece_count=720,
                min_age=10, base_price=109.99, stock_quantity=6,
                category_id=None,
                description="Scale model of the RMS Titanic ocean liner."),
    ]
    db.add_all(products)
    db.commit()
    print(f"Seed complete: {len(categories)} categories and {len(products)} products created.")


def seed(db: Session) -> None:
    seed_admin(db)
    seed_catalog(db)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
