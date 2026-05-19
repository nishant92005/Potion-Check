from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.deps import get_optional_user
from app.core.database import get_db
from app.models.entities import Analysis, ScanHistory, User, UserProfile
from app.schemas.schemas import AnalysisIn
from app.services.ai import analyze_ingredients

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


async def profile_dict(user: Optional[User], supplied: Optional[dict], db: AsyncSession) -> dict:
    if supplied:
        return supplied
    if user:
        profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
        if profile:
            return {"allergies": profile.allergies, "health_conditions": profile.health_conditions, "diet_type": profile.diet_type}
    return {"allergies": [], "health_conditions": [], "diet_type": "None"}


@router.post("/analyze")
async def analyze(payload: AnalysisIn, user: Optional[User] = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    product = payload.product_data or {}
    ingredients = payload.ingredients_text or product.get("ingredients_text") or ""
    profile = await profile_dict(user if payload.include_user_profile else None, payload.profile, db)
    ai = await analyze_ingredients(profile, ingredients, product.get("nutriments") or {})
    scan = ScanHistory(
        user_id=user.id if user else None,
        barcode=payload.barcode or product.get("barcode") or "TEXT",
        product_name=product.get("product_name") or "Ingredient Analysis",
        product_image_url=product.get("product_image_url") or product.get("image_front_url"),
        safety_score=ai["safety_score"],
        verdict=ai["verdict"],
        flagged_count=len(ai.get("flagged_ingredients", [])),
        raw_product_data=product
    )
    db.add(scan)
    await db.flush()
    analysis = Analysis(
        scan_id=scan.id,
        safety_score=ai["safety_score"],
        verdict=ai["verdict"],
        flagged_ingredients=ai.get("flagged_ingredients", []),
        all_ingredients=ai.get("all_ingredients", []),
        nutriments=ai.get("nutriments", product.get("nutriments") or {}),
        ai_summary=ai.get("ai_summary", ""),
        ai_recommendation=ai.get("ai_recommendation", ""),
        personalized_warnings=[flag.get("personalized_warning") for flag in ai.get("flagged_ingredients", [])]
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return {
        "analysis_id": analysis.id,
        "scan_id": scan.id,
        "barcode": scan.barcode,
        "product_name": scan.product_name,
        "brand": product.get("brands") or product.get("brand"),
        "categories": product.get("categories") or [],
        "product_image_url": scan.product_image_url,
        **ai
    }


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str, user: Optional[User] = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    analysis = await db.scalar(select(Analysis).where(Analysis.id == analysis_id))
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    scan = await db.get(ScanHistory, analysis.scan_id)
    if scan.user_id and (not user or scan.user_id != user.id):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"analysis_id": analysis.id, "scan_id": scan.id, "barcode": scan.barcode, "product_name": scan.product_name, "product_image_url": scan.product_image_url, "safety_score": analysis.safety_score, "verdict": analysis.verdict, "flagged_ingredients": analysis.flagged_ingredients, "all_ingredients": analysis.all_ingredients, "nutriments": analysis.nutriments, "ai_summary": analysis.ai_summary, "ai_recommendation": analysis.ai_recommendation}


@router.get("/product/{barcode}")
async def product_analysis(barcode: str, db: AsyncSession = Depends(get_db)):
    scan = await db.scalar(select(ScanHistory).where(ScanHistory.barcode == barcode).order_by(ScanHistory.created_at.desc()))
    if not scan:
        raise HTTPException(status_code=404, detail="No analysis for barcode")
    analysis = await db.scalar(select(Analysis).where(Analysis.scan_id == scan.id))
    return {"analysis_id": analysis.id, "scan_id": scan.id, "barcode": scan.barcode, "product_name": scan.product_name, "safety_score": analysis.safety_score, "verdict": analysis.verdict, "flagged_ingredients": analysis.flagged_ingredients, "all_ingredients": analysis.all_ingredients, "nutriments": analysis.nutriments, "ai_summary": analysis.ai_summary, "ai_recommendation": analysis.ai_recommendation}
