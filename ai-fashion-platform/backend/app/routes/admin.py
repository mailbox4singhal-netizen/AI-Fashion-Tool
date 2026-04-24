"""Admin dashboard — SRS §4.6 / FRS §3.3."""
import csv
import io
from collections import Counter

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.auth import require_admin
from app.database import get_db
from app.models import User, Request as ReqModel, AIResult, AuditLog, Config
from app.schemas import AdminMetrics, ConfigUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/metrics", response_model=AdminMetrics)
def metrics(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    total_requests = db.query(ReqModel).count()
    total_users = db.query(User).count()
    avg_conf = db.query(func.avg(AIResult.confidence)).scalar() or 0.0

    errored = db.query(ReqModel).filter(ReqModel.status.in_(["error", "low_confidence"])).count()
    error_rate = (errored / total_requests) if total_requests else 0.0

    regions = Counter()
    trend_names = Counter()
    buckets = {"0-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}

    for r in db.query(ReqModel).all():
        regions[(r.input_data or {}).get("region", "Unknown")] += 1

    for a in db.query(AIResult).filter(AIResult.module == "trend").all():
        for t in (a.output or {}).get("trends", []):
            trend_names[t.get("name", "Unknown")] += 1

    for a in db.query(AIResult).all():
        c = a.confidence or 0
        if c < 0.4:
            buckets["0-0.4"] += 1
        elif c < 0.6:
            buckets["0.4-0.6"] += 1
        elif c < 0.8:
            buckets["0.6-0.8"] += 1
        else:
            buckets["0.8-1.0"] += 1

    return {
        "total_requests": total_requests,
        "total_users": total_users,
        "avg_confidence": round(avg_conf, 3),
        "error_rate": round(error_rate, 3),
        "requests_by_region": dict(regions),
        "top_trends": [{"name": n, "count": c} for n, c in trend_names.most_common(5)],
        "confidence_distribution": buckets,
    }


@router.get("/audit-logs")
def audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    rows = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "request_id": r.request_id,
            "model_version": r.model_version,
            "prompt_version": r.prompt_version,
            "confidence": r.confidence,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/audit-logs/export")
def export_audit_logs(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    """FRS F10 CSV export."""
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(1000).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "request_id", "model_version", "prompt_version", "confidence", "created_at"])
    for r in rows:
        w.writerow([r.id, r.request_id, r.model_version, r.prompt_version, r.confidence, r.created_at.isoformat()])
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="audit_logs.csv"'},
    )


@router.get("/config")
def list_config(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return {row.key: row.value for row in db.query(Config).all()}


@router.post("/config")
def set_config(payload: ConfigUpdate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    row = db.query(Config).filter(Config.key == payload.key).first()
    if row:
        row.value = payload.value
    else:
        db.add(Config(key=payload.key, value=payload.value))
    db.commit()
    return {"ok": True}
