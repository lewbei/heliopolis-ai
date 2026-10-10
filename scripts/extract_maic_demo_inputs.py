"""Recover the two EXACT synthetic input PNGs embedded in the 8 Oct 2026 pitch.

Usage:
    python scripts/extract_maic_demo_inputs.py latest.pptx --output demo_inputs

This tool ONLY reads a local PPTX. It does not use Google Vertex, Internet
access, identifiable records or government data.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile, BadZipFile


EXPECTED = {
    "ppt/media/image2.png": (
        "01_SYNTHETIC_Perak_Land_Title.png",
        "8e3178cd01a4cf09a3b7ce017a0131f9368057f37e1b29c8638f601ea546f694",
    ),
    "ppt/media/image3.png": (
        "02_SYNTHETIC_MV_SLD_Auxiliary_Relay.png",
        "005f7bad7133e41c4fce758c73682486b6a4f5fc5365de76b62eae01d55f9246",
    ),
}


def extract(pptx: Path, output: Path) -> list[Path]:
    """Verify both source image hashes before writing them to disk."""
    recovered = []
    try:
        with ZipFile(pptx) as archive:
            for embedded, (name, expected_hash) in EXPECTED.items():
                content = archive.read(embedded)
                if hashlib.sha256(content).hexdigest() != expected_hash:
                    raise ValueError(
                        f"Image differs from the uploaded 8 October pitch: {embedded}. "
                        "Check that the correct PPTX version is being used."
                    )
                recovered.append((name, content))
    except (BadZipFile, KeyError) as exc:
        raise ValueError("PPTX is invalid or not the matching pitch version.") from exc

    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, content in recovered:
        destination = output / name
        destination.write_bytes(content)
        paths.append(destination)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--output", type=Path, default=Path("maic_demo_inputs"))
    arguments = parser.parse_args()
    for result in extract(arguments.pptx, arguments.output):
        print(f"Recovered {result} ({result.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
