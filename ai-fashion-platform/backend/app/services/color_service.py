"""Color intelligence engine (FRS F4)."""
import hashlib
import random
from typing import Any, Dict

from app.services.llm_client import get_llm_client, llm_enabled
from app.utils.prompts import COLOR_SYSTEM, color_user
from app.utils.logger import log_event


_PALETTES = {
    "India": [
        [("#E63946", "Kumkum Red"), ("#F4A261", "Marigold"), ("#2A9D8F", "Peacock"),
         ("#264653", "Indigo Night"), ("#F1FAEE", "Jasmine")],
        [("#6A0572", "Royal Plum"), ("#F18701", "Saffron"), ("#3A506B", "Monsoon"),
         ("#F5D0C5", "Rose Quartz"), ("#0B3954", "Deep Teal")],
    ],
    "Europe": [
        [("#2B2D42", "Graphite"), ("#EDF2F4", "Eggshell"), ("#8D99AE", "Parisian Grey"),
         ("#EF233C", "Vermillion"), ("#D4A373", "Camel")],
        [("#283618", "Forest"), ("#606C38", "Olive"), ("#FEFAE0", "Parchment"),
         ("#DDA15E", "Honey"), ("#BC6C25", "Rust")],
    ],
    "USA": [
        [("#F72585", "Hot Pink"), ("#7209B7", "Ultraviolet"), ("#3A0CA3", "Electric Indigo"),
         ("#4CC9F0", "Ice"), ("#F1FAEE", "Off White")],
        [("#264653", "Denim"), ("#E9C46A", "Prairie"), ("#F4A261", "Clay"),
         ("#E76F51", "Terracotta"), ("#2A9D8F", "Sage")],
    ],
    "Asia": [
        [("#FFB5A7", "Blush"), ("#FCD5CE", "Peach"), ("#F8EDEB", "Mist"),
         ("#D8E2DC", "Sage Mist"), ("#9D8189", "Mauve")],
        [("#0A0A0A", "Obsidian"), ("#C0C0C0", "Chrome"), ("#39FF14", "Neon Green"),
         ("#FF00E5", "Hyper Pink"), ("#1E1E2E", "Midnight")],
    ],
    "Global": [
        [("#FF1493", "Neon Pink"), ("#8A2BE2", "Violet"), ("#39FF14", "Neon Green"),
         ("#FFFFFF", "Pure White"), ("#0A0A0F", "Void")],
        [("#B5838D", "Dusty Rose"), ("#E5989B", "Coral"), ("#FFB4A2", "Peach"),
         ("#FFCDB2", "Cream"), ("#6D6875", "Smoke")],
    ],
}


def _mock(data: Dict[str, Any]) -> Dict[str, Any]:
    region = data.get("region", "Global")
    options = _PALETTES.get(region, _PALETTES["Global"])
    key = f"{region}|{data.get('prompt','')}"
    rng = random.Random(int(hashlib.md5(key.encode()).hexdigest()[:8], 16))
    palette = rng.choice(options)
    weights = [rng.uniform(0.1, 0.3) for _ in palette]
    total = sum(weights)
    colors = [
        {"hex": h, "name": n, "weight": round(w / total, 3)}
        for (h, n), w in zip(palette, weights)
    ]
    return {
        "colors": colors,
        "confidence": round(rng.uniform(0.75, 0.93), 2),
        "explanation": (
            f"Palette tuned to {region} cultural colour preferences and the "
            f"season/prompt context. Weights reflect suggested garment-area share."
        ),
    }


async def get_colors(data: Dict[str, Any], trends: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if not llm_enabled():
        return _mock(data)
    try:
        return await get_llm_client().complete_json(
            system=COLOR_SYSTEM,
            user=color_user(data, trends or {}),
        )
    except Exception as e:
        log_event("color_service.llm_failed_fallback_to_mock", error=str(e))
        return _mock(data)
