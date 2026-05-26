import re
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_optional_user
from app.core.database import get_db
from app.models.entities import Analysis, ScanHistory, User, UserProfile
from app.schemas.schemas import BarcodeAnalysisIn, BarcodeIn, TextIn
from app.services.ai import analyze_ingredients
from app.services.cache import cache_get, cache_set
from app.services.ocr import extract_ingredients_from_text, run_ocr
from app.services.open_food_facts import ProductLookupError, ProductNotFoundError, fetch_product
from app.services.serpapi import SerpApiLookupError, find_product_ingredients

router = APIRouter(prefix="/api/scanner", tags=["scanner"])
UPLOAD_DIR = Path("uploads")


async def profile_dict(user: Optional[User], supplied: Optional[dict], db: AsyncSession) -> dict:
    if supplied:
        return supplied
    if user:
        profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
        if profile:
            return {"allergies": profile.allergies, "health_conditions": profile.health_conditions, "diet_type": profile.diet_type}
    return {"allergies": [], "health_conditions": [], "diet_type": "None"}


def openfoodfacts_context(product: dict) -> str:
    parts = []
    if product.get("additives_tags"):
        parts.append(f"Additives detected by OpenFoodFacts: {', '.join(product['additives_tags'])}.")
    if product.get("allergens_tags"):
        parts.append(f"Allergens detected by OpenFoodFacts: {', '.join(product['allergens_tags'])}.")
    if product.get("nutrition_grades"):
        parts.append(f"Nutri-Score grade: {product['nutrition_grades']}.")
    if product.get("nova_group"):
        parts.append(f"NOVA processing group: {product['nova_group']}.")
    if product.get("categories"):
        parts.append(f"Categories: {', '.join(product['categories'][:6])}.")
    return "\n".join(parts)


async def get_cached_product(barcode: str) -> dict:
    key = f"off:{barcode}"
    cached = await cache_get(key)
    if cached:
        return cached
    product = await fetch_product(barcode)
    await cache_set(key, product, 86400)
    return product


async def get_serpapi_ingredients(barcode: str, product: Optional[dict] = None) -> dict:
    key = f"serpapi:ingredients:{barcode}"
    cached = await cache_get(key)
    if cached:
        return cached
    result = await find_product_ingredients(barcode, product)
    await cache_set(key, result, 86400)
    return result


async def enrich_product_from_google(barcode: str, product: Optional[dict] = None) -> dict:
    product = product or {"barcode": barcode, "product_name": f"Product {barcode}", "source": "serpapi_google_search"}
    search_data = await get_serpapi_ingredients(barcode, product)
    current_name = product.get("product_name")
    fallback_name = f"Product {barcode}"
    enriched = {
        **product,
        "barcode": barcode,
        "product_name": search_data.get("product_name") if current_name == fallback_name else current_name or search_data.get("product_name") or fallback_name,
        "ingredients_text": search_data["ingredients_text"],
        "ingredients_source": search_data["ingredients_source"],
        "serpapi_query": search_data.get("serpapi_query"),
        "serpapi_context": search_data.get("serpapi_context"),
        "source": f"{product.get('source') or 'openfoodfacts'}+serpapi",
    }
    return enriched


@router.post("/barcode")
async def barcode(payload: BarcodeIn):
    try:
        return await get_cached_product(payload.barcode)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Barcode product not found in OpenFoodFacts") from exc
    except ProductLookupError as exc:
        raise HTTPException(status_code=502, detail=str(exc) or "OpenFoodFacts lookup failed") from exc


@router.post("/barcode/analyze")
async def analyze_barcode(payload: BarcodeAnalysisIn, user: Optional[User] = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    off_error = None
    off_error_status = 404
    off_error_detail = "Barcode product not found in OpenFoodFacts"
    try:
        product = await get_cached_product(payload.barcode)
    except ProductNotFoundError as exc:
        off_error = exc
        product = {"barcode": payload.barcode, "product_name": f"Product {payload.barcode}", "source": "serpapi_google_search"}
    except ProductLookupError as exc:
        off_error = exc
        off_error_status = 502
        off_error_detail = str(exc) or "OpenFoodFacts lookup failed"
        product = {"barcode": payload.barcode, "product_name": f"Product {payload.barcode}", "source": "serpapi_google_search"}

    ingredients = product.get("ingredients_text") or ""
    serpapi_error = None
    if not ingredients:
        try:
            product = await enrich_product_from_google(payload.barcode, product)
            ingredients = product.get("ingredients_text") or ""
        except SerpApiLookupError as exc:
            serpapi_error = exc

    if off_error and not ingredients:
        raise HTTPException(status_code=off_error_status, detail=f"{off_error_detail}; SerpAPI fallback did not find ingredients") from off_error
    nutriments = product.get("nutriments") or product.get("nutrition") or {}
    if not ingredients:
        raise HTTPException(status_code=422, detail="Product found, but ingredients are missing in OpenFoodFacts") from serpapi_error

    profile = await profile_dict(user if payload.include_user_profile else None, payload.profile, db)
    product_context = openfoodfacts_context(product)
    if product.get("serpapi_context"):
        product_context = "\n".join(part for part in [product_context, f"Google search context from SerpAPI:\n{product['serpapi_context']}"] if part)
    ai = await analyze_ingredients(profile, ingredients, nutriments, product_context=product_context)
    scan = ScanHistory(
        user_id=user.id if user else None,
        barcode=payload.barcode,
        product_name=product.get("product_name") or f"Product {payload.barcode}",
        product_image_url=product.get("product_image_url") or product.get("image_front_url"),
        safety_score=ai["safety_score"],
        verdict=ai["verdict"],
        flagged_count=len(ai.get("flagged_ingredients", [])),
        raw_product_data=product,
    )
    db.add(scan)
    await db.flush()
    analysis = Analysis(
        scan_id=scan.id,
        safety_score=ai["safety_score"],
        verdict=ai["verdict"],
        flagged_ingredients=ai.get("flagged_ingredients", []),
        all_ingredients=ai.get("all_ingredients", []),
        nutriments=ai.get("nutriments", nutriments),
        ai_summary=ai.get("ai_summary", ""),
        ai_recommendation=ai.get("ai_recommendation", ""),
        personalized_warnings=[flag.get("personalized_warning") for flag in ai.get("flagged_ingredients", [])],
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
        "ingredients_text": ingredients,
        "nutrition": nutriments,
        "product_image_url": scan.product_image_url,
        **ai,
    }


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail="File must be an image")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=422, detail="File exceeds 10MB")
    UPLOAD_DIR.mkdir(exist_ok=True)
    suffix = Path(file.filename or "label.png").suffix or ".png"
    path = UPLOAD_DIR / f"{uuid.uuid4()}{suffix}"
    path.write_bytes(data)
    try:
        text = run_ocr(path)
    except Exception:
        text = ""
    return {"ingredients_text": text, "temp_file_path": str(path)}


@router.post("/text")
async def text(payload: TextIn):
    cleaned = extract_ingredients_from_text(payload.ingredients_text)
    tokens = [item.strip() for item in re.split(r",|;", cleaned) if item.strip()]
    return {"ingredients_text": cleaned, "ingredients": tokens}
