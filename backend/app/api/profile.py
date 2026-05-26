from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.entities import User, UserProfile
from app.schemas.schemas import ProfileIn, ProfileOut

router = APIRouter(prefix="/api/profile", tags=["profile"])

ALLOWED_ALLERGIES = {"Nuts", "Gluten", "Dairy", "Soy", "Eggs", "Shellfish", "Peanuts", "Fish"}
ALLOWED_CONDITIONS = {"Diabetes", "Hypertension", "Heart Disease", "Pregnant", "Kidney Disease", "Celiac Disease", "Lactose Intolerant", "None"}
ALLOWED_DIETS = {"Vegan", "Vegetarian", "None"}


@router.get("/", response_model=ProfileOut)
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if not profile:
        return ProfileOut(id=None, allergies=[], health_conditions=[], diet_type="None")
    return ProfileOut(id=profile.id, allergies=profile.allergies, health_conditions=profile.health_conditions, diet_type=profile.diet_type)


@router.post("/", response_model=ProfileOut)
async def save_profile(payload: ProfileIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    invalid_conditions = set(payload.health_conditions) - ALLOWED_CONDITIONS
    invalid_diet = payload.diet_type not in ALLOWED_DIETS
    if invalid_conditions or invalid_diet:
        raise HTTPException(status_code=422, detail="Invalid health profile value")
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
    profile.allergies = payload.allergies
    profile.health_conditions = payload.health_conditions
    profile.diet_type = payload.diet_type
    await db.commit()
    await db.refresh(profile)
    return ProfileOut(id=profile.id, allergies=profile.allergies, health_conditions=profile.health_conditions, diet_type=profile.diet_type)
