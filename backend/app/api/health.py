from datetime import datetime, timezone
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.cache import get_redis

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
async def health(db: AsyncSession = Depends(get_db)):
    status = {"database": "down", "redis": "down", "openfoodfacts": "down", "timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        await db.execute(text("select 1"))
        status["database"] = "ok"
    except Exception:
        pass
    try:
        await get_redis().ping()
        status["redis"] = "ok"
    except Exception:
        pass
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            await client.head("https://world.openfoodfacts.org")
        status["openfoodfacts"] = "ok"
    except Exception:
        pass
    return status
