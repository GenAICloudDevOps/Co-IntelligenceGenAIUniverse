from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[dict]:
        """Get user by username"""
        user = await User.get_by_username(username)
        return await user.to_dict() if user else None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[dict]:
        """Get user by email"""
        user = await User.get_by_email(email)
        return await user.to_dict() if user else None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[dict]:
        """Get user by ID"""
        user = await User.get_by_id(user_id)
        return await user.to_dict() if user else None

    @staticmethod
    async def create_user(name: str, email: str, username: str, password: str) -> dict:
        """Create a new user"""
        hashed_password = AuthService.get_password_hash(password)
        
        user = await User.create(
            name=name,
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            email_verified=False
        )
        
        return await user.to_dict()

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password"""
        user = await User.get_by_username(username)
        if not user:
            return None
        
        user_dict = await user.to_dict(exclude_password=False)
        if not AuthService.verify_password(password, user_dict["hashed_password"]):
            return None
        
        # Return user data without password
        return await user.to_dict(exclude_password=True)
