"""
Authentication API endpoints.
Handles user registration, login, and token management.
"""

import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from llm_pkg.auth.utils import (
    UserCreate,
    UserResponse,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_active_user,
    get_current_user,
)
from llm_pkg.database.models import User, get_db

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger("llm_pkg.auth")


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        db_user = create_user(db, user)
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """Authenticate user and return access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.post("/refresh-token")
async def refresh_access_token(current_user: User = Depends(get_current_user)):
    """Refresh access token for authenticated user."""
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
