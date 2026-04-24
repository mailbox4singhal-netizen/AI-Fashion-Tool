"""Tech-pack NLP generator (FRS F6)."""
import random
from typing import Any, Dict

from app.services.llm_client import get_llm_client, llm_enabled
from app.utils.prompts import TECHPACK_SYSTEM, techpack_user
from app.utils.logger import log_event


_CONSTRUCTION_BANK = [
    "French seams on all side panels",
    "Twin-needle topstitch along hem",
    "Raglan sleeve construction",
    "Bound neckline with self-fabric binding",
    "Inseam pockets reinforced with bartacks",
    "Rolled hem on sleeve cuffs",
    "Flat-fell seam at yoke",
]
_TRIMS = [
    "YKK metal zipper — matte black",
    "Corozo 4-hole button, 15L",
    "Satin woven main label, 30×50mm",
    "Recycled poly drawcord with metal tips",
    "Woven care label, side seam",
]


def _mock(data: Dict[str, Any], trends: Dict[str, Any]) -> Dict[str, Any]:
    rng = random.Random()
    category = (data.get("category") or "unisex").lower()
    trend_name = (trends.get("trends") or [{}])[0].get("name", "Modern Minimal")
    return {
        "tech_pack": {
            "title": f"{trend_name} — {category.title()} Piece",
            "category": category,
            "fabric": "Organic cotton jersey, 220 GSM",
            "colors": ["#F72585", "#7209B7", "#39FF14"],
            "construction": rng.sample(_CONSTRUCTION_BANK, k=4),
            "trims": rng.sample(_TRIMS, k=3),
            "measurements": {
                "chest": "106 cm", "length": "72 cm", "shoulder": "48 cm",
                "sleeve": "63 cm", "hem": "110 cm",
            },
            "care": [
                "Machine wash cold, inside out",
                "Do not bleach",
                "Tumble dry low",
                "Warm iron on reverse if needed",
            ],
        },
        "confidence": round(rng.uniform(0.78, 0.92), 2),
    }


async def generate_techpack(
    data: Dict[str, Any],
    trends: Dict[str, Any],
) -> Dict[str, Any]:
    if not llm_enabled():
        return _mock(data, trends)
    try:
        return await get_llm_client().complete_json(
            system=TECHPACK_SYSTEM,
            user=techpack_user(data, trends),
        )
    except Exception as e:
        log_event("techpack_service.llm_failed_fallback_to_mock", error=str(e))
        return _mock(data, trends)
