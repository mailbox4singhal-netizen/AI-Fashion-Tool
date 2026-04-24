"""Design routes — SRS §4.4, FRS F5.

RBAC: only designers/admins can refine designs; shoppers are view-only.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import require_designer_or_admin
from app.database import get_db
from app.models import User, AIResult
from app.schemas import DesignModifyRequest
from app.services.design_service import modify_design

router = APIRouter(prefix="/generate-design", tags=["design"])


@router.post("/modify")
async def modify(
    payload: DesignModifyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_designer_or_admin),
):
    rows = db.query(AIResult).filter(AIResult.module == "design").all()
    base = None
    for r in rows:
        if not isinstance(r.output, dict):
            continue
        for d in r.output.get("designs", []):
            if d.get("id") == payload.base_design_id:
                base = d
                break
        if base:
            break
    if not base:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Base design not found")
    return await modify_design(base, payload.modifier)
