"""Local, permission-gated live Gemini OCR smoke test (no PII output by default).

A human must still compare the extraction with the source. This command does
not calculate OCR accuracy or upload files to GitHub.

Usage:
    python verify_live_ocr.py --title /approved/local/title.png --confirm-cloud-processing
    python verify_live_ocr.py --sld /approved/local/sld.png --confirm-cloud-processing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import heliopolis_ocr
from solar_agent import DocumentReviewRequired, LandTitleParser, SLDTopologyResolver


def verify_document(
    path: Path,
    kind: str,
    *,
    confirm_cloud_processing: bool = False,
) -> dict[str, Any]:
    """Return only sanitized reliability/metadata; never store title-owner fields."""
    if kind not in ("TITLE", "SLD"):
        raise ValueError("Document kind must be TITLE or SLD.")
    if not confirm_cloud_processing:
        raise PermissionError(
            "Real scans will be sent to Google Gemini/Vertex AI. "
            "Run only with explicit permission and --confirm-cloud-processing."
        )
    if not (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
    ):
        raise RuntimeError(
            "No Gemini/Vertex credentials available. Set credentials in your "
            "local environment or .env; NEVER paste or commit API keys."
        )
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError("Supplied local image file does not exist.")
    if path.stat().st_size > 20_000_000:
        raise ValueError("Document exceeds the 20 MB local safeguard.")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {
        "status": "NEEDS_REVIEW",
        "document_sha256": digest,
        "document_type": kind,
        "model_configured": heliopolis_ocr.DEFAULT_MODEL,
        "source_type": "USER_SUPPLIED_DOCUMENT_UNVERIFIED",
        "independent_ground_truth_annotated": False,
        "field_level_accuracy": None,
        "no_legal_or_grid_approval": True,
        "cloud_transmission_user_confirmed": True,
    }
    try:
        if kind == "TITLE":
            meta = LandTitleParser.from_image(str(path))
            report["status"] = "STRUCTURED_EXTRACTION_NEEDS_HUMAN_CHECK"
            report["owner_count"] = len(meta.owners)
            report["area_positive"] = meta.area_sq_meters > 0
            report["land_review_status"] = meta.review_status
            report["field_level_accuracy"] = None  # no expert labels or independent comparison
        else:
            graph = SLDTopologyResolver().resolve_image(str(path))
            report["status"] = "TOPOLOGY_EXTRACTED_NEEDS_HUMAN_CHECK"
            report["node_count"] = graph.number_of_nodes()
            report["edge_count"] = graph.number_of_edges()
            report["modeled_topology_status"] = graph.graph["tnb_compliance"][
                "preliminary_topology_status"
            ]
    except (DocumentReviewRequired, ValueError) as exc:
        report["status"] = "NEEDS_REVIEW"
        report["review_reason"] = str(exc)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--title", type=Path)
    group.add_argument("--sld", type=Path)
    parser.add_argument(
        "--confirm-cloud-processing",
        action="store_true",
        help="Affirm permission to transmit supplied image to Google's service",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional local sanitized JSON audit path; do not commit raw source",
    )
    args = parser.parse_args()
    result = verify_document(
        args.title or args.sld,
        "TITLE" if args.title else "SLD",
        confirm_cloud_processing=args.confirm_cloud_processing,
    )
    formatted = json.dumps(result, indent=2)
    print(formatted)
    if args.output:
        args.output.write_text(formatted + "\n", encoding="utf-8")
    if result["status"] == "NEEDS_REVIEW":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
