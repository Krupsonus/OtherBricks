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
        Category(name="City", description="Urban scenes, emergency services and city life"),
        Category(name="Historical", description="Ancient civilisations and historical landmarks"),
    ]
    db.add_all(categories)
    db.flush()

    military = next(c for c in categories if c.name == "Military")
    arch = next(c for c in categories if c.name == "Architecture")
    vehicles = next(c for c in categories if c.name == "Vehicles")
    space = next(c for c in categories if c.name == "Space")
    city = next(c for c in categories if c.name == "City")
    historical = next(c for c in categories if c.name == "Historical")

    products = [
        # Military — Cobi
        Product(name="COBI Panzer IV Ausf. G", manufacturer="Cobi", piece_count=500,
                min_age=8, base_price=89.99, stock_quantity=20,
                category_id=military.id,
                description="Detailed 1:35 scale WWII Panzer IV tank with rotating turret and opening hatch."),
        Product(name="COBI Spitfire Mk.I", manufacturer="Cobi", piece_count=370,
                min_age=8, base_price=69.99, stock_quantity=15,
                category_id=military.id,
                description="Iconic British WWII fighter plane with stand and pilot figure."),
        Product(name="COBI T-34/85 Medium Tank", manufacturer="Cobi", piece_count=656,
                min_age=8, base_price=99.99, stock_quantity=10,
                category_id=military.id,
                description="Soviet T-34 tank with movable tracks, rotating turret and detailed engine cover."),
        Product(name="COBI USS Missouri Battleship", manufacturer="Cobi", piece_count=2211,
                min_age=14, base_price=259.99, stock_quantity=3,
                category_id=military.id,
                description="Large-scale WWII Iowa-class battleship with detailed deck and gun turrets."),
        Product(name="COBI P-51D Mustang", manufacturer="Cobi", piece_count=380,
                min_age=8, base_price=74.99, stock_quantity=12,
                category_id=military.id,
                description="American long-range WWII fighter with authentic markings and display stand."),

        # Architecture — CaDA, Oxford
        Product(name="CaDA Eiffel Tower", manufacturer="CaDA", piece_count=1050,
                min_age=12, base_price=129.99, stock_quantity=8,
                category_id=arch.id,
                description="Detailed micro-scale Eiffel Tower, approximately 60 cm tall when completed."),
        Product(name="CaDA Big Ben", manufacturer="CaDA", piece_count=890,
                min_age=12, base_price=109.99, stock_quantity=11,
                category_id=arch.id,
                description="Replica of the iconic London clock tower with intricate facade detail."),
        Product(name="Oxford Colosseum", manufacturer="Oxford", piece_count=1320,
                min_age=14, base_price=149.99, stock_quantity=6,
                category_id=arch.id,
                description="Impressive micro-scale model of the Roman Colosseum with interior detail."),

        # Vehicles — Mega Construx, CaDA, Oxford
        Product(name="Mega Construx Porsche 911 Turbo S", manufacturer="Mega Construx",
                piece_count=1288, min_age=14, base_price=199.99, stock_quantity=5,
                category_id=vehicles.id,
                description="Highly detailed Porsche 911 with opening hood, steerable front wheels and gearbox."),
        Product(name="CaDA Ferrari F40", manufacturer="CaDA", piece_count=1157,
                min_age=14, base_price=179.99, stock_quantity=7,
                category_id=vehicles.id,
                description="Classic 1987 Ferrari F40 with opening doors, removable engine cover and cockpit."),
        Product(name="Oxford Fire Engine", manufacturer="Oxford", piece_count=430,
                min_age=8, base_price=59.99, stock_quantity=18,
                category_id=vehicles.id,
                description="City fire engine with extending ladder, two firefighter figures and water cannon."),
        Product(name="CaDA Monster Truck", manufacturer="CaDA", piece_count=620,
                min_age=10, base_price=84.99, stock_quantity=14,
                category_id=vehicles.id,
                description="Oversized off-road monster truck with large suspension and pull-back motor."),
        Product(name="Oxford Rally Buggy", manufacturer="Oxford", piece_count=285,
                min_age=7, base_price=34.99, stock_quantity=25,
                category_id=vehicles.id,
                description="Compact off-road buggy with roll cage, driver figure and interchangeable tyres."),

        # Space — CaDA, Mega Construx
        Product(name="CaDA Space Shuttle Discovery", manufacturer="CaDA", piece_count=780,
                min_age=10, base_price=99.99, stock_quantity=12,
                category_id=space.id,
                description="NASA-inspired space shuttle with launch platform, opening cargo bay and satellite."),
        Product(name="Mega Construx Perseverance Rover", manufacturer="Mega Construx",
                piece_count=1173, min_age=14, base_price=159.99, stock_quantity=9,
                category_id=space.id,
                description="Accurate replica of NASA's Mars Perseverance rover with articulated arm and instruments."),
        Product(name="CaDA Saturn V Rocket", manufacturer="CaDA", piece_count=1969,
                min_age=16, base_price=219.99, stock_quantity=4,
                category_id=space.id,
                description="Towering Apollo-era Saturn V rocket with three separable stages and crew capsule."),

        # City — Oxford
        Product(name="Oxford Police Station", manufacturer="Oxford", piece_count=510,
                min_age=8, base_price=69.99, stock_quantity=16,
                category_id=city.id,
                description="Two-storey police station with garage, cell, three officer figures and patrol car."),
        Product(name="Oxford Corner Café", manufacturer="Oxford", piece_count=390,
                min_age=8, base_price=49.99, stock_quantity=22,
                category_id=city.id,
                description="Modular-style corner café with kitchen, seating area and three minifigures."),
        Product(name="Oxford Hospital", manufacturer="Oxford", piece_count=740,
                min_age=10, base_price=89.99, stock_quantity=9,
                category_id=city.id,
                description="Modern city hospital with reception, operating room, ambulance and medical staff."),

        # Historical — Oxford, CaDA
        Product(name="Oxford Egyptian Pyramid", manufacturer="Oxford", piece_count=820,
                min_age=10, base_price=94.99, stock_quantity=7,
                category_id=historical.id,
                description="Ancient Egyptian pyramid with hidden burial chamber, mummy and archaeologist figures."),
        Product(name="CaDA Medieval Castle", manufacturer="CaDA", piece_count=1560,
                min_age=12, base_price=189.99, stock_quantity=5,
                category_id=historical.id,
                description="Fortress with drawbridge, gatehouse, towers, catapult and twelve knight figures."),

        # No category — ships
        Product(name="COBI Titanic", manufacturer="Cobi", piece_count=720,
                min_age=10, base_price=109.99, stock_quantity=6,
                category_id=None,
                description="Scale model of the RMS Titanic ocean liner with detailed upper deck and funnels."),
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
