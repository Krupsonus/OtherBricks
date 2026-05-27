"""Database seed script.

Creates initial data required for the application to function:
- Default admin account (admin@otherbricks.com / admin123)

Run once after the database tables have been created:
    docker compose exec backend python seed.py
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
import models  # noqa: F401

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed(db: Session) -> None:
    from models.user import User, UserRole

    if db.query(User).filter(User.email == "admin@otherbricks.com").first():
        print("Seed already applied — skipping.")
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


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
