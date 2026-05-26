from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.entities import Analysis, ScanHistory, User

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/")
async def get_history(page: int = 1, limit: int = 20, filter: str = "all", search: str = "", user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(ScanHistory).where(ScanHistory.user_id == user.id)
    if filter != "all":
        stmt = stmt.where(ScanHistory.verdict == filter.upper())
    if search:
        stmt = stmt.where(ScanHistory.product_name.ilike(f"%{search}%"))
    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    scans = (await db.scalars(stmt.order_by(ScanHistory.created_at.desc()).offset((page - 1) * limit).limit(limit))).all()
    analysis_rows = (await db.scalars(select(Analysis).where(Analysis.scan_id.in_([scan.id for scan in scans])))).all() if scans else []
    analysis_by_scan = {analysis.scan_id: analysis for analysis in analysis_rows}
    return {
        "results": [{"id": scan.id, "scan_id": scan.id, "analysis_id": analysis_by_scan.get(scan.id).id if analysis_by_scan.get(scan.id) else None, "barcode": scan.barcode, "product_name": scan.product_name, "product_image_url": scan.product_image_url, "safety_score": scan.safety_score, "verdict": scan.verdict, "flagged_count": scan.flagged_count, "created_at": scan.created_at} for scan in scans],
        "total": total or 0,
        "page": page,
        "limit": limit
    }


@router.delete("/all")
async def delete_all(confirm: str = Query(...), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if confirm != user.email:
        raise HTTPException(status_code=400, detail="Confirmation must match user email")
    await db.execute(delete(ScanHistory).where(ScanHistory.user_id == user.id))
    await db.commit()
    return {"ok": True}


@router.delete("/{scan_id}")
async def delete_scan(scan_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    scan = await db.get(ScanHistory, scan_id)
    if not scan or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scan not found")
    await db.delete(scan)
    await db.commit()
    return {"ok": True}
