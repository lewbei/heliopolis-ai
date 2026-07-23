"""Gemini-powered OCR for Malaysian land title scans and single-line diagrams (SLD)."""

import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Use gemini-1.5-flash as the stable multimodal model.  The model name can be
# overridden via the GEMINI_MODEL environment variable.
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

_LAND_TITLE_PROMPT = """
You are an expert Malaysian land-title (Geran) OCR extractor.  Read the attached scanned land title image and return ONLY a JSON object with no markdown, no explanation, and no code fences.

Use these keys exactly:
{
  "title_no": "string or null",
  "lot_no": "string or null",
  "state": "Malaysian state name, e.g. Perak, Kedah, Selangor, or null",
  "district": "Daerah / District, or null",
  "mukim": "Mukim / sub-district, or null",
  "zoning": "Kategori Kegunaan Tanah, e.g. Pertanian, Bangunan, Perindustrian, or null",
  "area_acres": float or null,
  "area_roods": float or null,
  "area_poles": float or null,
  "has_caveats": true if a Caveat (Kaveat) is recorded, otherwise false,
  "has_charges": true if a Charge/Gadaian or Dichaj is recorded, otherwise false,
  "is_malay_reserve": true if Tanah Rezab Melayu / Malay Reserve appears, otherwise false,
  "owners": [
    {"name": "full name", "ic_or_co_no": "MyKad/SSM number", "share_fraction": "e.g. 11/120"}
  ]
}

If a field is unreadable, use null.  For owners, use an empty list if none are visible.  Share fractions are usually expressed as "X/120" in Malaysian titles.
"""

_SLD_PROMPT = """
You are an electrical engineering drawing OCR extractor.  Read the attached single-line diagram (SLD) image and return ONLY a JSON object with no markdown, no explanation, and no code fences.

Use these keys exactly:
{
  "symbols": [
    {"id": "unique_id", "class": "One of: PV_Array, Inverter, Anti_Islanding_Relay, Transformer, Grid_Connection", "bbox": [ymin, xmin, ymax, xmax]}
  ],
  "lines": [
    [[x1, y1], [x2, y2]]
  ]
}

The bbox values should be integer pixel coordinates [top, left, bottom, right].  Lines should connect symbol bounding boxes in the direction of power flow (PV -> Inverter -> Relay -> Transformer -> Grid).  If the relay is not drawn, omit the Anti_Islanding_Relay symbol and skip that segment.
"""


def _get_model():
    """Configure and return a Gemini generative model."""
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise RuntimeError(
            "google-generativeai is not installed. Run: pip install google-generativeai"
        ) from exc

    if not API_KEY:
        raise RuntimeError(
            "No Gemini API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment or .env file."
        )

    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(DEFAULT_MODEL)


def _extract_json(text: str) -> Optional[dict]:
    """Try to parse JSON from model output, stripping markdown fences if present."""
    if not text:
        return None

    # Strip markdown code fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Last resort: grab the first {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def _load_image(image_path: str | Path) -> Image.Image:
    """Open and convert an image to RGB for the Gemini API."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    return Image.open(path).convert("RGB")


def parse_land_title_image(image_path: str | Path) -> Optional[dict[str, Any]]:
    """
    Extract structured land-title metadata from an image using Gemini.

    Returns a dict with the fields requested in _LAND_TITLE_PROMPT, or None if
    the API call fails or the response cannot be parsed.
    """
    print(f"[HeliopolisOCR] Sending land title image to Gemini ({DEFAULT_MODEL})...")
    model = _get_model()
    image = _load_image(image_path)

    try:
        response = model.generate_content(
            [_LAND_TITLE_PROMPT, image],
            generation_config={"response_mime_type": "application/json"},
        )
    except Exception as exc:
        print(f"[HeliopolisOCR] Gemini API call failed: {exc}")
        return None

    return _extract_json(response.text)


def parse_sld_image(image_path: str | Path) -> Optional[dict[str, Any]]:
    """
    Extract SLD symbols and wire segments from an image using Gemini.

    Returns a dict with keys 'symbols' and 'lines', or None on failure.
    """
    print(f"[HeliopolisOCR] Sending SLD image to Gemini ({DEFAULT_MODEL})...")
    model = _get_model()
    image = _load_image(image_path)

    try:
        response = model.generate_content(
            [_SLD_PROMPT, image],
            generation_config={"response_mime_type": "application/json"},
        )
    except Exception as exc:
        print(f"[HeliopolisOCR] Gemini API call failed: {exc}")
        return None

    result = _extract_json(response.text)
    if result is None:
        return None

    # Normalise line endpoints from nested lists to tuples for downstream code.
    raw_lines = result.get("lines", [])
    normalised_lines = []
    for line in raw_lines:
        if len(line) == 2:
            normalised_lines.append(((float(line[0][0]), float(line[0][1])), (float(line[1][0]), float(line[1][1]))))
    result["lines"] = normalised_lines
    return result
