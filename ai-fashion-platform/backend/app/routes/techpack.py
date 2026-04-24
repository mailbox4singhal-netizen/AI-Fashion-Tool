"""Tech pack routes — SRS §4.5."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
import json

from app.auth import get_current_user
from app.database import get_db
from app.models import User, AIResult, Request as ReqModel

router = APIRouter(prefix="/generate-techpack", tags=["techpack"])


@router.get("/{request_id}")
def get_techpack(
    request_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = db.query(ReqModel).filter(ReqModel.id == request_id).first()
    if not req:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if req.user_id != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    tp = (
        db.query(AIResult)
        .filter(AIResult.request_id == request_id, AIResult.module == "techpack")
        .first()
    )
    if not tp or not isinstance(tp.output, dict):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tech pack not ready")
    return tp.output.get("tech_pack")


@router.get("/{request_id}/export")
def export_techpack(
    request_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export as downloadable JSON (FRS F6 'multi-format export')."""
    req = db.query(ReqModel).filter(ReqModel.id == request_id).first()
    if not req or (req.user_id != user.id and user.role != "admin"):
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    tp = (
        db.query(AIResult)
        .filter(AIResult.request_id == request_id, AIResult.module == "techpack")
        .first()
    )
    if not tp:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    payload = json.dumps(tp.output.get("tech_pack", {}), indent=2)
    return Response(
        content=payload,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="techpack_{request_id[:8]}.json"'},
    )
