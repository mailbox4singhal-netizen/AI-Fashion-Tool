"""AI Orchestrator — SRS §2 / §5.4 "Key Differentiator".

Responsibilities:
  - Fan out to trend / color / design / techpack services
  - Aggregate outputs + confidence
  - Apply confidence threshold + fallback logic
  - Persist DB records + audit logs with versioned prompts

Pipeline order:
  1. trends (no deps)
  2. colors (depends on trends for palette grounding)
  3. design + techpack (both depend on trends; designs also on colors)
"""
import asyncio
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Request, AIResult, AuditLog
from app.services.trend_service import get_trends
from app.services.color_service import get_colors
from app.services.design_service import generate_design
from app.services.nlp_service import generate_techpack
from app.services.llm_client import llm_enabled
from app.utils.prompts import PROMPT_VERSIONS, MODEL_VERSION
from app.utils.logger import log_event


async def process_request(
    db: Session,
    user_id: str,
    request_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    log_event(
        "orchestrator.start",
        request_id=request_id,
        user_id=user_id,
        llm_enabled=llm_enabled(),
    )

    req = Request(
        id=request_id,
        user_id=user_id,
        input_type="image+prompt" if data.get("image_url") else "prompt",
        input_data=data,
        status="processing",
    )
    db.add(req)
    db.commit()

    try:
        # 1. Trends first (colors will be grounded in them).
        trends = await get_trends(data)

        # 2. Colors + (design|techpack groundwork) can run in parallel once
        #    we have trends. Design also depends on colors, so run colors
        #    first, then fan out design + techpack.
        colors = await get_colors(data, trends)

        designs_out, techpack_out = await asyncio.gather(
            generate_design(data, trends, colors),
            generate_techpack(data, trends),
        )
    except Exception as e:
        req.status = "error"
        db.commit()
        log_event("orchestrator.error", request_id=request_id, error=str(e))
        raise

    confidences = [
        trends.get("confidence", 0.0) or 0.0,
        colors.get("confidence", 0.0) or 0.0,
        designs_out.get("confidence", 0.0) or 0.0,
        techpack_out.get("confidence", 0.0) or 0.0,
    ]
    avg_conf = sum(confidences) / len(confidences)

    for module, out, conf, pv in [
        ("trend",    trends,       trends.get("confidence"),       PROMPT_VERSIONS["trend"]),
        ("color",    colors,       colors.get("confidence"),       PROMPT_VERSIONS["color"]),
        ("design",   designs_out,  designs_out.get("confidence"),  PROMPT_VERSIONS["design"]),
        ("techpack", techpack_out, techpack_out.get("confidence"), PROMPT_VERSIONS["techpack"]),
    ]:
        db.add(AIResult(
            request_id=request_id,
            module=module,
            output=out,
            confidence=conf,
            explanation=out.get("explanation", ""),
        ))
        db.add(AuditLog(
            request_id=request_id,
            model_version=MODEL_VERSION,
            prompt_version=pv,
            input=data,
            output=out,
            confidence=conf,
        ))

    fallback = None
    if avg_conf < settings.confidence_threshold:
        fallback = (
            "Low confidence — try a clearer image, a more specific prompt, "
            "or narrow the region."
        )
        log_event("orchestrator.low_confidence",
                  request_id=request_id, confidence=avg_conf)

    req.status = "complete" if fallback is None else "low_confidence"
    db.commit()

    result = {
        "request_id": request_id,
        "status": req.status,
        "region": data.get("region", "Global"),
        "prompt": data.get("prompt", ""),
        "trends": trends.get("trends", []),
        "colors": colors.get("colors", []),
        "designs": designs_out.get("designs", []),
        "tech_pack": techpack_out.get("tech_pack"),
        "confidence": round(avg_conf, 3),
        "explanation": trends.get("explanation", ""),
        "fallback": fallback,
    }
    log_event("orchestrator.complete", request_id=request_id, confidence=avg_conf)
    return result


def load_result(db: Session, request_id: str) -> Dict[str, Any] | None:
    """Reassemble a past result from DB."""
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        return None

    by_module: Dict[str, AIResult] = {r.module: r for r in req.results}

    def pick(module: str, key: str, default):
        r = by_module.get(module)
        if not r or not isinstance(r.output, dict):
            return default
        return r.output.get(key, default)

    return {
        "request_id":  req.id,
        "status":      req.status,
        "region":      (req.input_data or {}).get("region", "Global"),
        "prompt":      (req.input_data or {}).get("prompt", ""),
        "trends":      pick("trend",    "trends",    []),
        "colors":      pick("color",    "colors",    []),
        "designs":     pick("design",   "designs",   []),
        "tech_pack":   pick("techpack", "tech_pack", None),
        "confidence":  round(
            sum((r.confidence or 0) for r in req.results) / max(len(req.results), 1), 3
        ),
        "explanation": pick("trend", "explanation", ""),
        "fallback":    None,
    }
