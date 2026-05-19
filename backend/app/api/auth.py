from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.entities import User
from app.schemas.schemas import TokenOut, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def user_out(user: User) -> UserOut:
    return UserOut(id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active)


@router.post("/register", status_code=201, response_model=TokenOut)
async def register(payload: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), full_name=payload.full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    access = create_token(user.id, timedelta(minutes=settings.access_token_expire_minutes))
    refresh = create_token(user.id, timedelta(days=settings.refresh_token_expire_days), "refresh")
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=settings.refresh_token_expire_days * 86400)
    return TokenOut(access_token=access, user=user_out(user))


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access = create_token(user.id, timedelta(minutes=settings.access_token_expire_minutes))
    refresh = create_token(user.id, timedelta(days=settings.refresh_token_expire_days), "refresh")
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=settings.refresh_token_expire_days * 86400)
    return TokenOut(access_token=access, user=user_out(user))


@router.post("/refresh")
async def refresh(request: Request):
    token = request.cookies.get("refresh_token")
    payload = decode_token(token or "")
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {"access_token": create_token(payload["sub"], timedelta(minutes=settings.access_token_expire_minutes)), "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user_out(user)
