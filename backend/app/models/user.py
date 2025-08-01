from tortoise.models import Model
from tortoise import fields
from datetime import datetime
from typing import Optional

class User(Model):
    """User model for authentication system"""
    
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=255, unique=True, index=True)
    username = fields.CharField(max_length=50, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)
    email_verified = fields.BooleanField(default=False)

    class Meta:
        table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        """Get user by username"""
        return await cls.filter(username=username, is_active=True).first()

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        """Get user by email"""
        return await cls.filter(email=email, is_active=True).first()

    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        return await cls.filter(id=user_id, is_active=True).first()

    async def to_dict(self, exclude_password: bool = True) -> dict:
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
        }
        
        if not exclude_password:
            data["hashed_password"] = self.hashed_password
            
        return data
