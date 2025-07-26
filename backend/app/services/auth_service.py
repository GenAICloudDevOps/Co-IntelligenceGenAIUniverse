from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.database import database
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
        query = """
        SELECT id, name, email, username, hashed_password, created_at, is_active, email_verified
        FROM users 
        WHERE username = :username AND is_active = true
        """
        result = await database.fetch_one(query=query, values={"username": username})
        return dict(result) if result else None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[dict]:
        """Get user by email"""
        query = """
        SELECT id, name, email, username, hashed_password, created_at, is_active, email_verified
        FROM users 
        WHERE email = :email AND is_active = true
        """
        result = await database.fetch_one(query=query, values={"email": email})
        return dict(result) if result else None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[dict]:
        """Get user by ID"""
        query = """
        SELECT id, name, email, username, created_at, is_active, email_verified
        FROM users 
        WHERE id = :user_id AND is_active = true
        """
        result = await database.fetch_one(query=query, values={"user_id": user_id})
        return dict(result) if result else None

    @staticmethod
    async def create_user(name: str, email: str, username: str, password: str) -> dict:
        """Create a new user"""
        hashed_password = AuthService.get_password_hash(password)
        
        query = """
        INSERT INTO users (name, email, username, hashed_password, created_at, is_active, email_verified)
        VALUES (:name, :email, :username, :hashed_password, NOW(), true, false)
        RETURNING id, name, email, username, created_at, is_active, email_verified
        """
        
        result = await database.fetch_one(
            query=query,
            values={
                "name": name,
                "email": email,
                "username": username,
                "hashed_password": hashed_password
            }
        )
        return dict(result)

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password"""
        user = await AuthService.get_user_by_username(username)
        if not user:
            return None
        
        if not AuthService.verify_password(password, user["hashed_password"]):
            return None
        
        # Remove hashed_password from returned user data
        user_data = {k: v for k, v in user.items() if k != "hashed_password"}
        return user_data
