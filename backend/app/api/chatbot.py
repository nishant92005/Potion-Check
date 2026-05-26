from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_current_user, get_optional_user
from app.core.database import get_db
from app.models.entities import Analysis, ScanHistory, User
from app.schemas.schemas import ChatQuestionIn
from app.services.rag import answer_product_question, index_product

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


async def user_scan(scan_id: str, user: Optional[User], db: AsyncSession) -> ScanHistory:
    scan = await db.get(ScanHistory, scan_id)
    if not scan or (scan.user_id and (not user or scan.user_id != user.id)):
        raise HTTPException(status_code=404, detail="Product history item not found")
    return scan


async def scan_analysis(scan_id: str, db: AsyncSession) -> Analysis:
    analysis = await db.scalar(select(Analysis).where(Analysis.scan_id == scan_id))
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis for this product was not found")
    return analysis


@router.get("/products")
async def products(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    scans = (
        await db.scalars(
            select(ScanHistory)
            .where(ScanHistory.user_id == user.id)
            .order_by(ScanHistory.created_at.desc())
            .limit(100)
        )
    ).all()
    if not scans:
        return {"results": []}
    analyses = (
        await db.scalars(
            select(Analysis).where(Analysis.scan_id.in_([scan.id for scan in scans]))
        )
    ).all()
    analysis_by_scan = {analysis.scan_id: analysis for analysis in analyses}
    return {
        "results": [
            {
                "scan_id": scan.id,
                "analysis_id": analysis_by_scan.get(scan.id).id if analysis_by_scan.get(scan.id) else None,
                "barcode": scan.barcode,
                "product_name": scan.product_name,
                "product_image_url": scan.product_image_url,
                "safety_score": scan.safety_score,
                "verdict": scan.verdict,
                "flagged_count": scan.flagged_count,
                "created_at": scan.created_at,
            }
            for scan in scans
            if analysis_by_scan.get(scan.id)
        ]
    }


@router.post("/index/{scan_id}")
async def index(scan_id: str, user: Optional[User] = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    scan = await user_scan(scan_id, user, db)
    analysis = await scan_analysis(scan.id, db)
    return await index_product(scan, analysis)


@router.post("/ask")
async def ask(payload: ChatQuestionIn, user: Optional[User] = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    scan = await user_scan(payload.scan_id, user, db)
    analysis = await scan_analysis(scan.id, db)
    return await answer_product_question(scan, analysis, payload.question)
