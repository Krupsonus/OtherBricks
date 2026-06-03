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


def seed_regular_user(db: Session) -> None:
    from models.user import User, UserRole

    if db.query(User).filter(User.email == "user@otherbricks.com").first():
        print("Regular user already exists — skipping.")
        return

    user = User(
        email="user@otherbricks.com",
        password_hash=pwd_context.hash("user123"),
        first_name="Jan",
        last_name="Kowalski",
        role=UserRole.user,
        is_active=True,
    )
    db.add(user)
    db.commit()
    print("Seed complete: user@otherbricks.com created.")


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

    # placehold.co colour palette per category (bg/text)
    IMG = {
        "military":    ("4a5e3a", "d4e8c2"),  # olive green
        "arch":        ("8b7355", "f5e6d0"),  # sandstone
        "vehicles":    ("2c5f8a", "c8dff5"),  # steel blue
        "space":       ("1a1a3e", "c0c8ff"),  # deep navy
        "city":        ("3a7ca5", "d0ecff"),  # sky blue
        "historical":  ("8b6914", "f5e6b0"),  # golden
        "none":        ("6b7280", "f3f4f6"),  # neutral grey
    }

    def img(key: str, label: str) -> str:
        bg, fg = IMG[key]
        text = label.replace(" ", "+")
        return f"https://placehold.co/400x400/{bg}/{fg}?text={text}"

    products = [
        # Military — Cobi
        Product(name="COBI Panzer IV Ausf. G", manufacturer="Cobi", piece_count=500,
                min_age=8, base_price=89.99, stock_quantity=20,
                category_id=military.id,
                image_url=img("military", "Panzer IV"),
                description="Detailed 1:35 scale WWII Panzer IV tank with rotating turret and opening hatch."),
        Product(name="COBI Spitfire Mk.I", manufacturer="Cobi", piece_count=370,
                min_age=8, base_price=69.99, stock_quantity=15,
                category_id=military.id,
                image_url=img("military", "Spitfire Mk.I"),
                description="Iconic British WWII fighter plane with stand and pilot figure."),
        Product(name="COBI T-34/85 Medium Tank", manufacturer="Cobi", piece_count=656,
                min_age=8, base_price=99.99, stock_quantity=10,
                category_id=military.id,
                image_url=img("military", "T-34/85"),
                description="Soviet T-34 tank with movable tracks, rotating turret and detailed engine cover."),
        Product(name="COBI USS Missouri Battleship", manufacturer="Cobi", piece_count=2211,
                min_age=14, base_price=259.99, stock_quantity=3,
                category_id=military.id,
                image_url=img("military", "USS Missouri"),
                description="Large-scale WWII Iowa-class battleship with detailed deck and gun turrets."),
        Product(name="COBI P-51D Mustang", manufacturer="Cobi", piece_count=380,
                min_age=8, base_price=74.99, stock_quantity=12,
                category_id=military.id,
                image_url=img("military", "P-51D Mustang"),
                description="American long-range WWII fighter with authentic markings and display stand."),

        # Architecture — CaDA, Oxford
        Product(name="CaDA Eiffel Tower", manufacturer="CaDA", piece_count=1050,
                min_age=12, base_price=129.99, stock_quantity=8,
                category_id=arch.id,
                image_url=img("arch", "Eiffel Tower"),
                description="Detailed micro-scale Eiffel Tower, approximately 60 cm tall when completed."),
        Product(name="CaDA Big Ben", manufacturer="CaDA", piece_count=890,
                min_age=12, base_price=109.99, stock_quantity=11,
                category_id=arch.id,
                image_url=img("arch", "Big Ben"),
                description="Replica of the iconic London clock tower with intricate facade detail."),
        Product(name="Oxford Colosseum", manufacturer="Oxford", piece_count=1320,
                min_age=14, base_price=149.99, stock_quantity=6,
                category_id=arch.id,
                image_url=img("arch", "Colosseum"),
                description="Impressive micro-scale model of the Roman Colosseum with interior detail."),

        # Vehicles — Mega Construx, CaDA, Oxford
        Product(name="Mega Construx Porsche 911 Turbo S", manufacturer="Mega Construx",
                piece_count=1288, min_age=14, base_price=199.99, stock_quantity=5,
                category_id=vehicles.id,
                image_url=img("vehicles", "Porsche 911"),
                description="Highly detailed Porsche 911 with opening hood, steerable front wheels and gearbox."),
        Product(name="CaDA Ferrari F40", manufacturer="CaDA", piece_count=1157,
                min_age=14, base_price=179.99, stock_quantity=7,
                category_id=vehicles.id,
                image_url=img("vehicles", "Ferrari F40"),
                description="Classic 1987 Ferrari F40 with opening doors, removable engine cover and cockpit."),
        Product(name="Oxford Fire Engine", manufacturer="Oxford", piece_count=430,
                min_age=8, base_price=59.99, stock_quantity=18,
                category_id=vehicles.id,
                image_url=img("vehicles", "Fire Engine"),
                description="City fire engine with extending ladder, two firefighter figures and water cannon."),
        Product(name="CaDA Monster Truck", manufacturer="CaDA", piece_count=620,
                min_age=10, base_price=84.99, stock_quantity=14,
                category_id=vehicles.id,
                image_url=img("vehicles", "Monster Truck"),
                description="Oversized off-road monster truck with large suspension and pull-back motor."),
        Product(name="Oxford Rally Buggy", manufacturer="Oxford", piece_count=285,
                min_age=7, base_price=34.99, stock_quantity=25,
                category_id=vehicles.id,
                image_url=img("vehicles", "Rally Buggy"),
                description="Compact off-road buggy with roll cage, driver figure and interchangeable tyres."),

        # Space — CaDA, Mega Construx
        Product(name="CaDA Space Shuttle Discovery", manufacturer="CaDA", piece_count=780,
                min_age=10, base_price=99.99, stock_quantity=12,
                category_id=space.id,
                image_url=img("space", "Space Shuttle"),
                description="NASA-inspired space shuttle with launch platform, opening cargo bay and satellite."),
        Product(name="Mega Construx Perseverance Rover", manufacturer="Mega Construx",
                piece_count=1173, min_age=14, base_price=159.99, stock_quantity=9,
                category_id=space.id,
                image_url=img("space", "Perseverance"),
                description="Accurate replica of NASA's Mars Perseverance rover with articulated arm and instruments."),
        Product(name="CaDA Saturn V Rocket", manufacturer="CaDA", piece_count=1969,
                min_age=16, base_price=219.99, stock_quantity=4,
                category_id=space.id,
                image_url=img("space", "Saturn V"),
                description="Towering Apollo-era Saturn V rocket with three separable stages and crew capsule."),

        # City — Oxford
        Product(name="Oxford Police Station", manufacturer="Oxford", piece_count=510,
                min_age=8, base_price=69.99, stock_quantity=16,
                category_id=city.id,
                image_url=img("city", "Police Station"),
                description="Two-storey police station with garage, cell, three officer figures and patrol car."),
        Product(name="Oxford Corner Café", manufacturer="Oxford", piece_count=390,
                min_age=8, base_price=49.99, stock_quantity=22,
                category_id=city.id,
                image_url=img("city", "Corner Cafe"),
                description="Modular-style corner café with kitchen, seating area and three minifigures."),
        Product(name="Oxford Hospital", manufacturer="Oxford", piece_count=740,
                min_age=10, base_price=89.99, stock_quantity=9,
                category_id=city.id,
                image_url=img("city", "Hospital"),
                description="Modern city hospital with reception, operating room, ambulance and medical staff."),

        # Historical — Oxford, CaDA
        Product(name="Oxford Egyptian Pyramid", manufacturer="Oxford", piece_count=820,
                min_age=10, base_price=94.99, stock_quantity=7,
                category_id=historical.id,
                image_url=img("historical", "Pyramid"),
                description="Ancient Egyptian pyramid with hidden burial chamber, mummy and archaeologist figures."),
        Product(name="CaDA Medieval Castle", manufacturer="CaDA", piece_count=1560,
                min_age=12, base_price=189.99, stock_quantity=5,
                category_id=historical.id,
                image_url=img("historical", "Medieval Castle"),
                description="Fortress with drawbridge, gatehouse, towers, catapult and twelve knight figures."),

        # No category — ships
        Product(name="COBI Titanic", manufacturer="Cobi", piece_count=720,
                min_age=10, base_price=109.99, stock_quantity=6,
                category_id=None,
                image_url=img("none", "Titanic"),
                description="Scale model of the RMS Titanic ocean liner with detailed upper deck and funnels."),
    ]
    db.add_all(products)
    db.commit()
    print(f"Seed complete: {len(categories)} categories and {len(products)} products created.")


def seed_price_offers(db: Session) -> None:
    """Add sample external price offers for all products."""
    from models.price_offer import PriceOffer
    from models.product import Product

    if db.query(PriceOffer).first():
        print("Price offers already seeded — skipping.")
        return

    all_products = {p.name: p for p in db.query(Product).all()}

    def o(name, shop, url, price):
        p = all_products.get(name)
        return PriceOffer(product_id=p.id, shop_name=shop, shop_url=url, price=price) if p else None

    raw = [
        # Military
        o("COBI Panzer IV Ausf. G",      "BrickLink",    "https://www.bricklink.com",    84.50),
        o("COBI Panzer IV Ausf. G",      "Amazon",       "https://www.amazon.com",        87.99),
        o("COBI Panzer IV Ausf. G",      "Smyths Toys",  "https://www.smythstoys.com",    92.00),

        o("COBI Spitfire Mk.I",          "COBI Official","https://cobi.pl",               65.99),
        o("COBI Spitfire Mk.I",          "BrickLink",    "https://www.bricklink.com",    68.50),
        o("COBI Spitfire Mk.I",          "eBay",         "https://www.ebay.com",          72.00),

        o("COBI T-34/85 Medium Tank",    "COBI Official","https://cobi.pl",               94.99),
        o("COBI T-34/85 Medium Tank",    "Amazon",       "https://www.amazon.com",        97.50),
        o("COBI T-34/85 Medium Tank",    "Smyths Toys",  "https://www.smythstoys.com",   102.00),

        o("COBI USS Missouri Battleship","COBI Official","https://cobi.pl",              249.99),
        o("COBI USS Missouri Battleship","BrickLink",    "https://www.bricklink.com",   239.00),
        o("COBI USS Missouri Battleship","Amazon",       "https://www.amazon.com",       254.95),

        o("COBI P-51D Mustang",          "COBI Official","https://cobi.pl",               69.99),
        o("COBI P-51D Mustang",          "Amazon",       "https://www.amazon.com",        72.49),
        o("COBI P-51D Mustang",          "eBay",         "https://www.ebay.com",          76.00),

        # Architecture
        o("CaDA Eiffel Tower",           "CADA Official","https://www.cada-block.com",   119.99),
        o("CaDA Eiffel Tower",           "Amazon",       "https://www.amazon.com",       124.50),
        o("CaDA Eiffel Tower",           "eBay",         "https://www.ebay.com",         125.00),

        o("CaDA Big Ben",                "CADA Official","https://www.cada-block.com",   104.99),
        o("CaDA Big Ben",                "AliExpress",   "https://www.aliexpress.com",    89.99),
        o("CaDA Big Ben",                "Amazon",       "https://www.amazon.com",       109.00),

        o("Oxford Colosseum",            "Oxford Toys",  "https://www.oxfordtoys.com",   144.99),
        o("Oxford Colosseum",            "Amazon",       "https://www.amazon.com",       149.99),
        o("Oxford Colosseum",            "eBay",         "https://www.ebay.com",         139.00),

        # Vehicles
        o("Mega Construx Porsche 911 Turbo S","Mattel Shop","https://www.mattel.com",    199.99),
        o("Mega Construx Porsche 911 Turbo S","Amazon",   "https://www.amazon.com",      189.95),
        o("Mega Construx Porsche 911 Turbo S","Zavvi",    "https://www.zavvi.com",       209.99),

        o("CaDA Ferrari F40",            "CADA Official","https://www.cada-block.com",   169.99),
        o("CaDA Ferrari F40",            "AliExpress",   "https://www.aliexpress.com",   149.99),
        o("CaDA Ferrari F40",            "Amazon",       "https://www.amazon.com",       174.50),

        o("Oxford Fire Engine",          "Oxford Toys",  "https://www.oxfordtoys.com",    57.99),
        o("Oxford Fire Engine",          "Smyths Toys",  "https://www.smythstoys.com",    59.99),
        o("Oxford Fire Engine",          "Amazon",       "https://www.amazon.com",        62.50),

        o("CaDA Monster Truck",          "CADA Official","https://www.cada-block.com",    79.99),
        o("CaDA Monster Truck",          "AliExpress",   "https://www.aliexpress.com",    69.99),
        o("CaDA Monster Truck",          "eBay",         "https://www.ebay.com",          82.00),

        o("Oxford Rally Buggy",          "Oxford Toys",  "https://www.oxfordtoys.com",    32.99),
        o("Oxford Rally Buggy",          "Smyths Toys",  "https://www.smythstoys.com",    34.99),
        o("Oxford Rally Buggy",          "Amazon",       "https://www.amazon.com",        36.50),

        # Space
        o("CaDA Space Shuttle Discovery","CADA Official","https://www.cada-block.com",    94.99),
        o("CaDA Space Shuttle Discovery","AliExpress",   "https://www.aliexpress.com",    79.99),
        o("CaDA Space Shuttle Discovery","Amazon",       "https://www.amazon.com",        98.50),

        o("Mega Construx Perseverance Rover","Mattel Shop","https://www.mattel.com",     159.99),
        o("Mega Construx Perseverance Rover","Amazon",   "https://www.amazon.com",       152.00),
        o("Mega Construx Perseverance Rover","eBay",     "https://www.ebay.com",         164.99),

        o("CaDA Saturn V Rocket",        "CADA Official","https://www.cada-block.com",   209.99),
        o("CaDA Saturn V Rocket",        "AliExpress",   "https://www.aliexpress.com",   189.99),
        o("CaDA Saturn V Rocket",        "Amazon",       "https://www.amazon.com",       214.50),

        # City
        o("Oxford Police Station",       "Oxford Toys",  "https://www.oxfordtoys.com",    64.99),
        o("Oxford Police Station",       "Smyths Toys",  "https://www.smythstoys.com",    69.99),
        o("Oxford Police Station",       "Amazon",       "https://www.amazon.com",        67.50),

        o("Oxford Corner Café",          "Oxford Toys",  "https://www.oxfordtoys.com",    46.99),
        o("Oxford Corner Café",          "Smyths Toys",  "https://www.smythstoys.com",    49.99),
        o("Oxford Corner Café",          "Amazon",       "https://www.amazon.com",        51.00),

        o("Oxford Hospital",             "Oxford Toys",  "https://www.oxfordtoys.com",    84.99),
        o("Oxford Hospital",             "Smyths Toys",  "https://www.smythstoys.com",    89.99),
        o("Oxford Hospital",             "Amazon",       "https://www.amazon.com",        86.50),

        # Historical
        o("Oxford Egyptian Pyramid",     "Oxford Toys",  "https://www.oxfordtoys.com",    89.99),
        o("Oxford Egyptian Pyramid",     "Amazon",       "https://www.amazon.com",        94.99),
        o("Oxford Egyptian Pyramid",     "eBay",         "https://www.ebay.com",          91.50),

        o("CaDA Medieval Castle",        "CADA Official","https://www.cada-block.com",   179.99),
        o("CaDA Medieval Castle",        "BrickLink",    "https://www.bricklink.com",    175.00),
        o("CaDA Medieval Castle",        "Amazon",       "https://www.amazon.com",       185.49),

        # No category
        o("COBI Titanic",               "COBI Official","https://cobi.pl",              104.99),
        o("COBI Titanic",               "BrickLink",    "https://www.bricklink.com",    99.50),
        o("COBI Titanic",               "Smyths Toys",  "https://www.smythstoys.com",   109.99),
    ]

    offers = [item for item in raw if item is not None]
    db.add_all(offers)
    db.commit()
    print(f"Seed complete: {len(offers)} price offers created.")


def seed(db: Session) -> None:
    seed_admin(db)
    seed_regular_user(db)
    seed_catalog(db)
    seed_price_offers(db)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
