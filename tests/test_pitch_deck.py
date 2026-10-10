from pathlib import Path

from generate_pitch_deck import build, parse_slides


def test_pitch_source_has_nine_numbered_slides():
    source = Path(__file__).resolve().parents[1] / "PITCH_DECK.md"
    slides = parse_slides(source.read_text(encoding="utf-8"))
    assert len(slides) == 9
    assert [s.number for s in slides] == list(range(1, 10))
    assert slides[0].title == "Heliopolis-AI"
    assert all(s.lines for s in slides)


def test_generated_pdf_uses_updated_source_and_is_nontrivial(tmp_path):
    source = Path(__file__).resolve().parents[1] / "PITCH_DECK.md"
    target = tmp_path / "pitch.pdf"
    slide_count, page_count = build(source, target)
    assert slide_count == 9
    assert 9 <= page_count <= 15
    assert target.read_bytes().startswith(b"%PDF")
    assert target.stat().st_size > 10_000
