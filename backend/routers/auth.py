"""
/auth endpoints: register and login.

Design:
- POST /auth/register creates a User with a bcrypt-hashed password.
  Returns 400 if the email is already taken (checked explicitly rather
  than relying only on the DB unique-constraint error, so we can return
  a clean message instead of a raw IntegrityError).
- POST /auth/login verifies credentials and returns a JWT bearer token.
  We return a generic "invalid credentials" message on both wrong-email
  and wrong-password cases, to avoid leaking which emails are registered.
- get_current_user is an OAuth2PasswordBearer-based dependency other
  routers (e.g. documents.py) use to require auth on protected routes.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User
from schemas.user import Token, UserCreate, UserLogin, UserOut
from security import create_access_token, decode_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        logger.info("Registration attempt with existing email: %s", payload.email)
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to create user")
        raise HTTPException(status_code=500, detail="Could not create user")

    await db.refresh(user)
    logger.info("User registered: %s", user.id)
    return user


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        logger.info("Failed login attempt for email: %s", payload.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=user.id)
    logger.info("User logged in: %s", user.id)
    return Token(access_token=token)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency for protected routes. Raises 401 on any auth failure."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user
