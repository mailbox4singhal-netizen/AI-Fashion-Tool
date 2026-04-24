"""AI Design Studio — concept generation (FRS F5)."""
import hashlib
import random
import uuid
from typing import Any, Dict, List

from app.services.llm_client import get_llm_client, llm_enabled
from app.utils.prompts import (
    DESIGN_SYSTEM,
    DESIGN_MODIFY_SYSTEM,
    design_user,
    design_modify_user,
)
from app.utils.logger import log_event


_SILHOUETTES = {
    "women": ["A-line midi", "Boxy cropped", "Drop-shoulder oversized",
              "Fitted bodice flared hem", "Column silhouette", "Asymmetric wrap"],
    "men":   ["Relaxed straight", "Slim tapered", "Boxy cropped",
              "Elongated overshirt", "Pleated trouser", "Deconstructed blazer"],
    "kids":  ["Easy raglan", "Elasticated waist", "Playful ruffled",
              "Boxy tee", "Pinafore", "Jumper dress"],
    "unisex":["Boxy oversized", "Straight-leg trouser", "Utility cargo",
              "Longline overshirt", "Zip-through hoodie", "Cropped cardigan"],
}
_FABRICS = [
    "Organic cotton jersey", "Recycled polyester twill", "Linen-blend weave",
    "Bamboo-viscose knit", "Brushed fleece", "Satin-finish crepe",
    "Dead-stock denim", "Seersucker", "Silk-cotton blend",
]


def _ensure_ids(designs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """LLMs sometimes return short/duplicate ids — force real uuids."""
    for d in designs:
        d["id"] = str(uuid.uuid4())
    return designs


def _mock(data: Dict[str, Any], trends: Dict[str, Any], colors: Dict[str, Any]) -> Dict[str, Any]:
    key = f"{data.get('region','')}-{data.get('prompt','')}-{data.get('category','')}"
    rng = random.Random(int(hashlib.sha1(key.encode()).hexdigest()[:8], 16))
    category = (data.get("category") or "unisex").lower()
    sil_pool = _SILHOUETTES.get(category, _SILHOUETTES["unisex"])
    trend_names = [t["name"] for t in trends.get("trends", [])][:3] or ["Modern Minimal"]
    hex_palette = [c["hex"] for c in colors.get("colors", [])][:4]

    designs = []
    for i in range(3):
        trend = trend_names[i % len(trend_names)]
        designs.append({
            "id": str(uuid.uuid4()),
            "title": f"{trend} — Look {i + 1:02d}",
            "summary": f"A {rng.choice(sil_pool).lower()} piece informed by the "
                       f"'{trend}' direction, sized for {category}.",
            "silhouette": rng.choice(sil_pool),
            "fabric": rng.choice(_FABRICS),
            "palette": hex_palette,
        })
    return {"designs": designs, "confidence": round(rng.uniform(0.70, 0.90), 2)}


async def generate_design(
    data: Dict[str, Any],
    trends: Dict[str, Any],
    colors: Dict[str, Any],
) -> Dict[str, Any]:
    if not llm_enabled():
        return _mock(data, trends, colors)
    try:
        out = await get_llm_client().complete_json(
            system=DESIGN_SYSTEM,
            user=design_user(data, trends, colors),
        )
        out["designs"] = _ensure_ids(out.get("designs", []))
        return out
    except Exception as e:
        log_event("design_service.llm_failed_fallback_to_mock", error=str(e))
        return _mock(data, trends, colors)


async def modify_design(base: Dict[str, Any], modifier: str) -> Dict[str, Any]:
    """F5 refinement — 'more formal', 'pastel version', 'shorter hem'..."""
    if not llm_enabled():
        modified = dict(base)
        modified["id"] = str(uuid.uuid4())
        modified["title"] = f"{base.get('title', 'Design')} · {modifier.title()}"
        modified["summary"] = f"{base.get('summary', '')} Applied modifier: {modifier}."
        return modified

    try:
        out = await get_llm_client().complete_json(
            system=DESIGN_MODIFY_SYSTEM,
            user=design_modify_user(base, modifier),
        )
        out["id"] = str(uuid.uuid4())
        return out
    except Exception as e:
        log_event("design_service.modify_llm_failed", error=str(e))
        # fall back to simple annotation
        modified = dict(base)
        modified["id"] = str(uuid.uuid4())
        modified["title"] = f"{base.get('title', 'Design')} · {modifier.title()}"
        return modified
