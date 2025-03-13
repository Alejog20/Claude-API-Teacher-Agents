"""
Authentication routes for user registration, login, and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, TokenData
from app.db.database import get_db
from app.db import crud
from app.services.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    validate_email_password
)
from app.utils.config import settings
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("auth_routes")

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db = Depends(get_db)):
    """
    Register a new user.
    """
    # Validate user data
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if username already exists
    existing_user = await crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = await crud.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = await crud.create_user(db, user_data)
    
    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    """
    Authenticate user and provide access token.
    """
    # Find user by username
    user = await crud.get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": user["username"],
        "user_id": user["id"]
    }
    access_token = create_access_token(
        data=token_data, 
        expires_delta=access_token_expires
    )
    
    # Get expires_at datetime
    now = datetime.utcnow()
    expires_at = now + access_token_expires
    
    # Get user data for response
    user_response = UserResponse(**user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": user_response
    }

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db = Depends(get_db)):
    """
    Alternative login endpoint using JSON request body instead of form data.
    """
    # Find user by username
    user = await crud.get_user_by_username(db, login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": user["username"],
        "user_id": user["id"]
    }
    access_token = create_access_token(
        data=token_data, 
        expires_delta=access_token_expires
    )
    
    # Get expires_at datetime
    now = datetime.utcnow()
    expires_at = now + access_token_expires
    
    # Get user data for response
    user_response = UserResponse(**user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": user_response
    }

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    """
    Get the current authenticated user from token.
    
    This is a dependency that can be used in other routes to get the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await crud.get_user(db, user_id)
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    """
    return current_user

@router.post("/refresh")
async def refresh_token(current_user = Depends(get_current_user)):
    """
    Refresh the current access token.
    """
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": current_user["username"],
        "user_id": current_user["id"]
    }
    access_token = create_access_token(
        data=token_data, 
        expires_delta=access_token_expires
    )
    
    # Get expires_at datetime
    now = datetime.utcnow()
    expires_at = now + access_token_expires
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }

@router.post("/change-password")
async def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    confirm_password: str = Body(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Change the password for the current user.
    """
    # Validate new password
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Verify current password
    if not verify_password(current_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Update password
    user_update = {"password": new_password}
    updated_user = await crud.update_user(db, current_user["id"], user_update)
    
    return {"message": "Password changed successfully"}