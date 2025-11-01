"""
User Repository
Data access layer for User operations
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.domain.user import User


class UserRepository:
    """Repository for User CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user: User) -> User:
        """Create a new user."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Update an existing user."""
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()
