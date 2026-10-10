"""Gemini-powered OCR for Malaysian land title scans and single-line diagrams (SLD).

Authentication order:
  1. AI Studio / API key: GEMINI_API_KEY or GOOGLE_API_KEY
  2. Vertex AI: GOOGLE_CLOUD_PROJECT (+ optional GOOGLE_CLOUD_LOCATION, default us-central1)
  3. Failure returns None (uploaded-document caller MUST fail closed; no demo substitution)
"""

import io
import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Current GA model; legacy gemini-1.5-flash-002 was shut down in 2025.
# Override GEMINI_MODEL if your project/region uses a different supported deployment.
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

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
  "area_hectares_stated": float or null,
  "area_sq_meters_stated": float or null,
  "has_caveats": true if a Caveat (Kaveat) is recorded, false if legibly absent, null if unreadable,
  "has_charges": true if a Charge/Gadaian or Dichaj is recorded, false if legibly absent, null if unreadable,
  "is_malay_reserve": true if Tanah Rezab Melayu / Malay Reserve appears, false if legibly absent, null if unreadable,
  "owners": [
    {"name": "full name", "ic_or_co_no": "MyKad/SSM number", "share_fraction": "e.g. 11/120"}
  ]
}

Only report area_hectares_stated/area_sq_meters_stated when independently printed on the scanned source; NEVER calculate them from Ekar/Rood/Pole. These are cross-check fields, not solver outputs.\n\nNever infer that a land restriction is absent from illegible text: return null for unknown flags. If an owner section is unreadable or not shown, return an empty list; do not invent owners.  Share fractions are usually expressed as "X/120" in Malaysian titles.
"""

_SLD_PROMPT = """
You are an electrical engineering drawing OCR extractor.  Read the attached single-line diagram (SLD) image and return ONLY a JSON object with no markdown, no explanation, and no code fences.

Use these keys exactly:
{
  "symbols": [
    {
      "id": "unique_id",
      "class": "One of: PV_Array, Inverter, AC_Switch, PV_Meter, Anti_Islanding_Relay, Transformer, Grid_Connection, Junction_Dot",
      "bbox": [ymin, xmin, ymax, xmax],
      "integrated_anti_islanding_label": null,
      "anti_islanding_source_text": null
    }
  ],
  "lines": [
    [[x1, y1], [x2, y2]]
  ],
  "junction_dots": [
    [x, y]
  ]
}

The bbox values should be integer pixel coordinates [top, left, bottom, right].
Extract ONLY printed symbols and visible wire endpoints. Never invent an external relay,
transformer or wire segment to match an assumed PV -> Inverter -> Grid topology.
For LV drawings, a separate transformer or relay may not be illustrated.
Represent visible AC isolator/main switches as AC_Switch and PV meters as
PV_Meter, preserving their actual wiring. Identify the utility L/N/E or L1/L2/L3
incoming boundary as Grid_Connection, never as a guessed transformer.
A generic inverter symbol DOES NOT establish anti-islanding. Set
integrated_anti_islanding_label to true ONLY when an anti-islanding / non-islanding
inverter label (or IEC 62116 annotation) is visibly printed with the inverter,
and quote those exact words in anti_islanding_source_text. Otherwise use null
for both fields (do not infer an inverter certificate from context).
For other symbol categories set those optional fields to null.

Junction dots (small filled circles) are electrical connection points.  Return a junction dot coordinate wherever two or more line segments are physically joined.  Do NOT return a junction dot where two lines simply cross without an explicit connection.  If the SLD contains a Junction_Dot symbol, include it in the symbols list instead of junction_dots.
"""


def _get_client() -> tuple[Any, str]:
    """
    Build and return a google-genai Client plus a short label describing the
    authentication backend ("api_key" or "vertex").  Raises RuntimeError if no
    usable credentials are found.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install google-genai"
        ) from exc

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if project:
        return (
            genai.Client(vertexai=True, project=project, location=location),
            "vertex",
        )

    if api_key:
        return genai.Client(api_key=api_key), "api_key"

    raise RuntimeError(
        "No Gemini credentials found. Set GOOGLE_CLOUD_PROJECT (+ GOOGLE_CLOUD_LOCATION) "
        "for Vertex AI, or GEMINI_API_KEY / GOOGLE_API_KEY for AI Studio."
    )


def _image_to_part(image: Image.Image):
    """Convert a PIL image to a google-genai Part with PNG bytes."""
    from google.genai import types

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")


def _extract_json(text: str) -> Optional[dict[str, Any]]:
    """Try to parse JSON from model output, stripping markdown fences if present."""
    if not text:
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def _generate_json(prompt: str, image: Image.Image) -> Optional[dict[str, Any]]:
    """Send one prompt + image to Gemini and parse JSON from the response."""
    from google.genai import types

    try:
        client, backend = _get_client()
    except RuntimeError as exc:
        print(f"[HeliopolisOCR] {exc}")
        return None

    print(f"[HeliopolisOCR] Using Gemini backend: {backend} ({DEFAULT_MODEL})")

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=[prompt, _image_to_part(image)],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
    except Exception as exc:
        print(f"[HeliopolisOCR] Gemini request failed ({type(exc).__name__}); output requires review.")
        return None

    return _extract_json(response.text)


def parse_land_title_image(image_path: str | Path) -> Optional[dict[str, Any]]:
    """
    Extract structured land-title metadata from an image using Gemini.

    Returns a dict with the fields requested in _LAND_TITLE_PROMPT, or None if
    the call fails or the response cannot be parsed.
    """
    print(f"[HeliopolisOCR] Sending land title image to Gemini ({DEFAULT_MODEL})...")
    path = Path(image_path)
    if not path.exists():
        print(f"[HeliopolisOCR] Image not found: {image_path}")
        return None
    try:
        with Image.open(path) as opened:
            image = opened.convert("RGB")
    except (OSError, ValueError, Image.DecompressionBombError):
        print("[HeliopolisOCR] Invalid or unreadable uploaded image; manual review required.")
        return None
    return _generate_json(_LAND_TITLE_PROMPT, image)


def parse_sld_image(image_path: str | Path) -> Optional[dict[str, Any]]:
    """
    Extract SLD symbols and wire segments from an image using Gemini.

    Returns a dict with keys 'symbols' and 'lines', or None on failure.
    """
    print(f"[HeliopolisOCR] Sending SLD image to Gemini ({DEFAULT_MODEL})...")
    path = Path(image_path)
    if not path.exists():
        print(f"[HeliopolisOCR] Image not found: {image_path}")
        return None
    try:
        with Image.open(path) as opened:
            image = opened.convert("RGB")
    except (OSError, ValueError, Image.DecompressionBombError):
        print("[HeliopolisOCR] Invalid or unreadable uploaded image; manual review required.")
        return None
    result = _generate_json(_SLD_PROMPT, image)
    if result is None:
        return None

    # Reject malformed geometry as unreadable; never fabricate a safe graph.
    try:
        if not isinstance(result, dict):
            return None
        symbols = result.get("symbols")
        raw_lines = result.get("lines")
        raw_dots = result.get("junction_dots", [])
        if not isinstance(symbols, list) or not isinstance(raw_lines, list) or not isinstance(raw_dots, list):
            return None
        normalized_lines = []
        for line in raw_lines:
            if not isinstance(line, list) or len(line) != 2:
                return None
            a, b = line
            if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)) or len(a) != 2 or len(b) != 2:
                return None
            normalized_lines.append(((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))))
        normalized_dots = []
        for dot in raw_dots:
            if not isinstance(dot, (list, tuple)) or len(dot) != 2:
                return None
            normalized_dots.append((float(dot[0]), float(dot[1])))
        result["lines"] = normalized_lines
        result["junction_dots"] = normalized_dots
        return result
    except (ValueError, TypeError, IndexError):
        return None
