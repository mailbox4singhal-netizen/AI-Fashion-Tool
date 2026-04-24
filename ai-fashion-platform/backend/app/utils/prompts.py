"""Versioned prompts — SRS §5.5 / FRS §8.

Each prompt has:
  • a SYSTEM message defining the engine's role
  • a user-template function returning the per-request user message
  • an output schema written directly into the system prompt, so the LLM
    returns strict JSON that matches what `schemas.py` expects.

Every audit log row records the PROMPT_VERSION used for the call.
Bump the version string when you change a prompt.
"""
from typing import Any, Dict

MODEL_VERSION = "orchestrator-1.1.0"

PROMPT_VERSIONS = {
    "trend":    "V1.3.0",
    "color":    "V1.2.0",
    "design":   "V1.4.0",
    "techpack": "V1.1.0",
}


# =========================================================================
# TREND (F2)
# =========================================================================
TREND_SYSTEM = """You are a fashion trend forecaster for a global retail platform.
Your job is to predict 3 emerging trends for a given region + prompt context.

You MUST respond with ONLY valid JSON, no markdown fences, no preamble. Schema:
{
  "trends": [
    {"name": "<short trend title>", "forecast": "<one-sentence direction>", "growth": <number 0-1>}
  ],
  "confidence": <number 0-1>,
  "explanation": "<2-3 sentence rationale grounded in consumer signals>"
}

Rules:
- Exactly 3 trends.
- `growth` = predicted year-over-year growth fraction (e.g. 0.23 = +23%).
- Trends must feel specific to the region's consumer culture and the prompt.
- `confidence` reflects your overall certainty.
"""


def trend_user(data: Dict[str, Any]) -> str:
    return (
        f"Region: {data.get('region', 'Global')}\n"
        f"Category: {data.get('category', 'unisex')}\n"
        f"Season: {data.get('season', 'current')}\n"
        f"Prompt: {data.get('prompt', '')}\n"
        f"{'Inspiration image URL: ' + data['image_url'] if data.get('image_url') else ''}\n\n"
        "Predict the 3 top emerging fashion trends for this context."
    )


# =========================================================================
# COLOR (F4)
# =========================================================================
COLOR_SYSTEM = """You are a color intelligence engine for fashion design.
Given a region + prompt + season, you propose a culturally appropriate,
trend-aware palette of exactly 5 colors.

You MUST respond with ONLY valid JSON, no markdown fences. Schema:
{
  "colors": [
    {"hex": "#RRGGBB", "name": "<evocative name>", "weight": <0-1>}
  ],
  "confidence": <0-1>,
  "explanation": "<2-3 sentence rationale>"
}

Rules:
- Exactly 5 colors.
- Weights should sum to approximately 1.0 — they represent suggested
  garment-area share.
- All hex codes must be valid #RRGGBB uppercase.
- Names should feel editorial (e.g. "Saffron Dusk", not "Orange 3").
"""


def color_user(data: Dict[str, Any], trends: Dict[str, Any]) -> str:
    trend_names = [t.get("name", "") for t in (trends.get("trends") or [])]
    return (
        f"Region: {data.get('region', 'Global')}\n"
        f"Season: {data.get('season', 'current')}\n"
        f"Category: {data.get('category', 'unisex')}\n"
        f"Prompt: {data.get('prompt', '')}\n"
        f"Active trends: {', '.join(trend_names) if trend_names else 'n/a'}\n\n"
        "Propose a 5-color palette tuned to this context."
    )


# =========================================================================
# DESIGN (F5)
# =========================================================================
DESIGN_SYSTEM = """You are an AI design director for a fashion-tech platform.
Given trends + a palette + a brief, you produce 3 distinct garment concepts.

You MUST respond with ONLY valid JSON, no markdown fences. Schema:
{
  "designs": [
    {
      "id": "<unique short id>",
      "title": "<concept name>",
      "summary": "<1-2 sentence elevator pitch>",
      "silhouette": "<silhouette descriptor>",
      "fabric": "<fabric + GSM or finish>",
      "palette": ["#RRGGBB", "#RRGGBB", "#RRGGBB"]
    }
  ],
  "confidence": <0-1>
}

Rules:
- Exactly 3 designs, each visually distinct.
- `palette` = 3-4 hex codes drawn from the provided palette (reuse is fine).
- Titles should feel like a designer named them, not generic.
- Adapt silhouettes to the requested category (women/men/kids/unisex).
"""


def design_user(data: Dict[str, Any], trends: Dict[str, Any], colors: Dict[str, Any]) -> str:
    trend_names = [t.get("name", "") for t in (trends.get("trends") or [])]
    hexes = [c.get("hex", "") for c in (colors.get("colors") or [])]
    return (
        f"Brief: {data.get('prompt', '')}\n"
        f"Region: {data.get('region', 'Global')}\n"
        f"Category: {data.get('category', 'unisex')}\n"
        f"Season: {data.get('season', 'current')}\n"
        f"Trends to reflect: {', '.join(trend_names)}\n"
        f"Palette: {', '.join(hexes)}\n\n"
        "Generate 3 design concepts."
    )


DESIGN_MODIFY_SYSTEM = """You are an AI design director. Given a base design
and a natural-language modifier (e.g. "make it more formal", "pastel version",
"shorter hem"), produce a refined design.

Respond with ONLY valid JSON. Schema:
{
  "id": "<new unique id>",
  "title": "<updated title reflecting the modifier>",
  "summary": "<updated summary>",
  "silhouette": "<possibly-updated silhouette>",
  "fabric": "<possibly-updated fabric>",
  "palette": ["#RRGGBB", "#RRGGBB", "#RRGGBB"]
}
"""


def design_modify_user(base: Dict[str, Any], modifier: str) -> str:
    return (
        f"Base design:\n"
        f"  title: {base.get('title', '')}\n"
        f"  summary: {base.get('summary', '')}\n"
        f"  silhouette: {base.get('silhouette', '')}\n"
        f"  fabric: {base.get('fabric', '')}\n"
        f"  palette: {base.get('palette', [])}\n\n"
        f"Modifier: {modifier}\n\n"
        "Return the refined design."
    )


# =========================================================================
# TECH PACK (F6)
# =========================================================================
TECHPACK_SYSTEM = """You are a technical designer generating an industry-
standard garment tech pack. Given the brief and the top trend, produce a
production-ready spec.

You MUST respond with ONLY valid JSON, no markdown fences. Schema:
{
  "tech_pack": {
    "title": "<garment title>",
    "category": "<women|men|kids|unisex>",
    "fabric": "<fabric name + GSM>",
    "colors": ["#RRGGBB", "#RRGGBB", "#RRGGBB"],
    "construction": ["<detail 1>", "<detail 2>", "..."],
    "trims": ["<trim 1>", "<trim 2>", "..."],
    "measurements": {
      "chest": "<e.g. 106 cm>",
      "length": "<cm>",
      "shoulder": "<cm>",
      "sleeve": "<cm>",
      "hem": "<cm>"
    },
    "care": ["<instruction 1>", "..."]
  },
  "confidence": <0-1>
}

Rules:
- 3-5 construction notes, 3-5 trim specs, 3-4 care instructions.
- Measurements should be realistic for the category.
"""


def techpack_user(data: Dict[str, Any], trends: Dict[str, Any]) -> str:
    top_trend = (trends.get("trends") or [{}])[0].get("name", "Modern Minimal")
    return (
        f"Category: {data.get('category', 'unisex')}\n"
        f"Region: {data.get('region', 'Global')}\n"
        f"Season: {data.get('season', 'current')}\n"
        f"Brief: {data.get('prompt', '')}\n"
        f"Leading trend: {top_trend}\n\n"
        "Generate a production-ready tech pack."
    )
