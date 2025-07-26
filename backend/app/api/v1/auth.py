from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.auth import (
    UserRegister, 
    UserLogin, 
    UserResponse, 
    Token, 
    LoginResponse, 
    RegisterResponse
)
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import get_current_active_user
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """Register a new user"""
    
    # Check if username already exists
    existing_user = await AuthService.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = await AuthService.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create user
        user = await AuthService.create_user(
            name=user_data.name,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = AuthService.create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        
        return RegisterResponse(
            user=UserResponse(**user),
            token=Token(access_token=access_token),
            message="Registration successful"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
async def login_user(user_credentials: UserLogin):
    """Login user with username and password"""
    
    # Authenticate user
    user = await AuthService.authenticate_user(
        username=user_credentials.username,
        password=user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        user=UserResponse(**user),
        token=Token(access_token=access_token),
        message="Login successful"
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_active_user)):
    """Logout user (client should remove token)"""
    return {
        "message": "Logout successful",
        "detail": "Please remove the token from client storage"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: dict = Depends(get_current_active_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": current_user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)
