"""Stage artifact constraints published in MAIC Nexus 2026 official FAQ.

These tests only check the DRAFT branch's proposed source documents; they
cannot check the user's already-submitted portal artifacts or review lock.
"""
import re
from pathlib import Path

from generate_pitch_deck import build, parse_slides


ROOT = Path(__file__).resolve().parents[1]


def test_maic_draft_project_summary_under_500_words():
    raw = (ROOT / "qrspi" / "PROJECT_SUMMARY.md").read_text(encoding="utf-8")
    # Count URL tokens conservatively; excluding Markdown punctuation only.
    normalized = re.sub(r"[#*_|>]", " ", raw).replace(chr(96), " ")
    words = [token for token in normalized.split() if token.strip()]
    assert len(words) <= 500, f"MAIC official max 500 words, draft has {len(words)}"


def test_maic_draft_pdf_under_12_pages_and_5mb(tmp_path):
    source = ROOT / "PITCH_DECK.md"
    sections = parse_slides(source.read_text(encoding="utf-8"))
    assert 1 <= len(sections) <= 12
    output = tmp_path / "maic-proposed-pitch.pdf"
    _, pages = build(source, output)
    assert pages <= 12, f"MAIC official max 12 pages/slides; draft renders {pages}"
    assert output.stat().st_size <= 5_000_000, "MAIC max 5 MB PDF"
