# Import all models here so they are registered with SQLAlchemy Base
# and picked up by Base.metadata.create_all() in main.py
from .user import User  # noqa: F401
from .category import Category  # noqa: F401
from .product import Product  # noqa: F401
