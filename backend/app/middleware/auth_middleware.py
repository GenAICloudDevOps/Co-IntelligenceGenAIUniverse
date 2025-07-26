from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth_service import AuthService

# Security scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = AuthService.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Get user from database
    user = await AuthService.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != "hashed_password"}
    return user_data

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current active user"""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Optional authentication - doesn't raise error if no token
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """Get current user if token is provided, otherwise return None"""
    if not credentials:
        return None
    
    try:
        payload = AuthService.verify_token(credentials.credentials)
        if payload is None:
            return None
        
        username: str = payload.get("sub")
        if username is None:
            return None
            
        user = await AuthService.get_user_by_username(username)
        if user is None:
            return None
        
        user_data = {k: v for k, v in user.items() if k != "hashed_password"}
        return user_data
        
    except Exception:
        return None
