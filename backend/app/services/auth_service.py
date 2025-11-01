"""
Authentication Service
Business logic for user authentication and JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
import os

from app.domain.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import UserCreate, TokenData

# Password hashing - using bcrypt directly to avoid passlib compatibility issues
BCRYPT_ROUNDS = 12

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password. Bcrypt has a 72 byte limit."""
        # Bcrypt has a maximum password length of 72 bytes
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = self.user_repo.find_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            if username is None:
                return None
            return TokenData(username=username, user_id=user_id)
        except JWTError:
            return None

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if username or email already exists
        if self.user_repo.find_by_username(user_data.username):
            raise ValueError(f"Username '{user_data.username}' already exists")
        if self.user_repo.find_by_email(user_data.email):
            raise ValueError(f"Email '{user_data.email}' already exists")

        # Create user with hashed password
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=self.get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False
        )
        return self.user_repo.create(user)

    def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a JWT token."""
        token_data = self.decode_access_token(token)
        if token_data is None or token_data.username is None:
            return None

        user = self.user_repo.find_by_username(token_data.username)
        if user is None or not user.is_active:
            return None

        return user
