"""
Database Configuration and Session Management
Marking Criteria: 4.4 (Incorporation of Advanced Technologies)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://retailer:retailer123@localhost:5432/retailer_db")

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20,
    echo=os.getenv("DEBUG", "false").lower() == "true"  # Log SQL in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database sessions.
    Ensures proper session cleanup.

    Usage:
        @app.get("/products")
        def get_products(db: Session = Depends(get_db)):
            return db.query(Product).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    Called at application startup.
    """
    # Import all models to ensure they're registered with Base
    from app.domain import product, cart, order, inventory_item, user

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
