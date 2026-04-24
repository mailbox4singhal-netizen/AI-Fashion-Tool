"""Analyze + results — SRS §4.2 / §4.3.

RBAC:
  POST /analyze         → designer, admin (shoppers cannot create)
  GET  /results/{id}    → any logged-in user (own requests; admin sees all)
  GET  /my/history      → any logged-in user (their own)
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_designer_or_admin
from app.database import get_db
from app.models import User, Request as ReqModel
from app.schemas import AnalyzeRequest, ResultResponse
from app.services.orchestrator import process_request, load_result

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=ResultResponse)
async def analyze(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_designer_or_admin),   # RBAC
):
    """Kick off the full pipeline. Restricted to designers/admins."""
    request_id = str(uuid.uuid4())
    return await process_request(db, user.id, request_id, payload.model_dump())


@router.get("/results/{request_id}", response_model=ResultResponse)
def get_results(
    request_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = db.query(ReqModel).filter(ReqModel.id == request_id).first()
    if not req:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Request not found")
    if req.user_id != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your request")
    return load_result(db, request_id)


@router.get("/my/history")
def history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reqs = (
        db.query(ReqModel)
        .filter(ReqModel.user_id == user.id)
        .order_by(ReqModel.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "request_id": r.id,
            "prompt": (r.input_data or {}).get("prompt", ""),
            "region": (r.input_data or {}).get("region", ""),
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in reqs
    ]
