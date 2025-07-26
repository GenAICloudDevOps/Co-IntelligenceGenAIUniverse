from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('username')
    def username_must_be_valid(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only letters and numbers')
        return v.lower()

    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    username: str
    created_at: datetime
    is_active: bool
    email_verified: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginResponse(BaseModel):
    user: UserResponse
    token: Token
    message: str = "Login successful"

class RegisterResponse(BaseModel):
    user: UserResponse
    token: Token
    message: str = "Registration successful"
