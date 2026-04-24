"""Trend prediction engine (FRS F2/F3).

If an LLM provider is configured, calls the LLM with the versioned
TREND prompt and parses its JSON response. Otherwise, returns a
deterministic mock so the app runs offline.
"""
import hashlib
import random
from typing import Any, Dict

from app.services.llm_client import get_llm_client, llm_enabled
from app.utils.prompts import TREND_SYSTEM, trend_user
from app.utils.logger import log_event


# ----- Mock data ---------------------------------------------------------
_TREND_BANK = {
    "India": [
        ("Festive Ethnic Fusion", "Rising demand through festive season", 0.28),
        ("Neo-Tropical Prints",   "Monsoon collections trending up",      0.19),
        ("Handloom Revival",      "Steady growth in premium segment",     0.14),
        ("Indo-Streetwear",       "Breakout category for Gen Z",          0.33),
    ],
    "Europe": [
        ("Quiet Luxury 2.0",      "Stable demand in premium",             0.11),
        ("Upcycled Denim",        "Sustainability-led growth",            0.22),
        ("Editorial Minimalism",  "Editorial press cycle peak",           0.09),
        ("Avant-Folk Tailoring",  "Niche but accelerating",               0.17),
    ],
    "USA": [
        ("Athflow Layering",      "Post-athleisure evolution",            0.24),
        ("Y2K Nostalgia Edit",    "Gen Z anchor trend",                   0.31),
        ("Workwear Reinterpreted","Steady core demand",                   0.13),
        ("Pastel Prep",           "Spring/Summer breakout",               0.20),
    ],
    "Asia": [
        ("Soft Cyber",            "Rapid growth across K-fashion",        0.35),
        ("Techwear Lite",         "Urban commuter staple",                0.21),
        ("Modern Hanbok Cues",    "Premium cultural crossover",           0.18),
        ("Oversized Prep",        "Campus-driven momentum",               0.14),
    ],
    "Global": [
        ("Gorpcore Refined",      "Outdoor crossover into city wear",     0.25),
        ("Chrome Futurism",       "Editorial + clubwear convergence",     0.19),
        ("Soft Tailoring",        "Workwear humanized",                   0.16),
        ("Bio-Textiles Spotlight","Sustainability leader trend",          0.22),
    ],
}


def _mock(data: Dict[str, Any]) -> Dict[str, Any]:
    region = data.get("region", "Global")
    pool = _TREND_BANK.get(region, _TREND_BANK["Global"])
    key = f"{region}|{data.get('prompt','')}|{data.get('category','')}"
    rng = random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:8], 16))
    picks = rng.sample(pool, k=min(3, len(pool)))
    trends = [
        {"name": n, "forecast": f, "growth": round(g + rng.uniform(-0.03, 0.05), 3)}
        for n, f, g in picks
    ]
    return {
        "trends": trends,
        "confidence": round(rng.uniform(0.72, 0.94), 2),
        "explanation": (
            f"Based on {region} market signals and the prompt "
            f"\"{data.get('prompt','')}\", regional consumer data, "
            f"social-media signal velocity, and retail search volume "
            f"surface these 3 trends."
        ),
    }


# ----- Public API --------------------------------------------------------
async def get_trends(data: Dict[str, Any]) -> Dict[str, Any]:
    if not llm_enabled():
        return _mock(data)
    try:
        return await get_llm_client().complete_json(
            system=TREND_SYSTEM,
            user=trend_user(data),
        )
    except Exception as e:
        log_event("trend_service.llm_failed_fallback_to_mock", error=str(e))
        return _mock(data)
