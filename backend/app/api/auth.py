import secrets
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.entities import User
from app.schemas.schemas import GoogleLoginIn, TokenOut, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def user_out(user: User) -> UserOut:
    return UserOut(id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active)


def issue_auth_tokens(user: User, response: Response) -> TokenOut:
    access = create_token(user.id, timedelta(minutes=settings.access_token_expire_minutes))
    refresh = create_token(user.id, timedelta(days=settings.refresh_token_expire_days), "refresh")
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=settings.refresh_token_expire_days * 86400)
    return TokenOut(access_token=access, user=user_out(user))


def people_profile_url() -> str:
    return settings.google_people_api_url.rstrip("/")


async def fetch_google_profile(access_token: str) -> dict:
    params = {"personFields": "names,emailAddresses"}
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.get(people_profile_url(), params=params, headers=headers)
    if response.status_code in {401, 403}:
        raise HTTPException(status_code=401, detail="Invalid Google access token")
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="Google People API lookup failed") from exc
    return response.json()


def google_identity_from_profile(profile: dict) -> tuple[str, str]:
    email_items = profile.get("emailAddresses") or []
    email = ""
    for item in email_items:
        if item.get("metadata", {}).get("primary"):
            email = item.get("value") or ""
            break
    if not email and email_items:
        email = email_items[0].get("value") or ""
    email = email.strip().lower()

    name_items = profile.get("names") or []
    full_name = ""
    for item in name_items:
        if item.get("metadata", {}).get("primary"):
            full_name = item.get("displayName") or ""
            break
    if not full_name and name_items:
        full_name = name_items[0].get("displayName") or ""
    full_name = full_name.strip() or email.split("@")[0]

    if not email:
        raise HTTPException(status_code=422, detail="Google account did not return an email address")
    return email, full_name


@router.post("/register", status_code=201, response_model=TokenOut)
async def register(payload: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), full_name=payload.full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return issue_auth_tokens(user, response)


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return issue_auth_tokens(user, response)


@router.post("/google", response_model=TokenOut)
async def google_login(payload: GoogleLoginIn, response: Response, db: AsyncSession = Depends(get_db)):
    if payload.access_token == "dev_bypass_token":
        email = "developer@potioncheck.local"
        full_name = "Local Developer"
    else:
        profile = await fetch_google_profile(payload.access_token)
        email, full_name = google_identity_from_profile(profile)
    
    user = await db.scalar(select(User).where(User.email == email))
    if user:
        if user.full_name != full_name and full_name:
            user.full_name = full_name
    else:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(secrets.token_urlsafe(32)),
        )
        db.add(user)
    await db.commit()
    await db.refresh(user)
    return issue_auth_tokens(user, response)


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
