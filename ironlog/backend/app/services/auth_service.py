"""Authentication service."""
from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return pwd_context.hash(password_bytes)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return pwd_context.verify(password_bytes, hashed_password)


def create_access_token(user_id: UUID) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": str(user_id), "type": "access", "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: UUID) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {"sub": str(user_id), "type": "refresh", "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UUID | None:
    """Decode and validate access token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        return UUID(user_id) if user_id else None
    except JWTError:
        return None


def decode_refresh_token(token: str) -> UUID | None:
    """Decode and validate refresh token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            return None
        user_id = payload.get("sub")
        return UUID(user_id) if user_id else None
    except JWTError:
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password: str, display_name: str | None = None) -> User:
    """Create a new user."""
    hashed_password = hash_password(password)
    user = User(email=email, password_hash=hashed_password, display_name=display_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate user by email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
