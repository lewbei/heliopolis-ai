"""Test the pitch-media extractor without committing or exposing the actual source PPTX."""
import hashlib
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts import extract_maic_demo_inputs as extractor


def test_two_sources_extracted_only_when_both_hashes_match(tmp_path, monkeypatch):
    first, second = b"not real title media", b"not real electrical drawing"
    specs = {
        "ppt/media/image2.png": ("title.png", hashlib.sha256(first).hexdigest()),
        "ppt/media/image3.png": ("sld.png", hashlib.sha256(second).hexdigest()),
    }
    monkeypatch.setattr(extractor, "EXPECTED", specs)
    pptx = tmp_path / "synthetic_test.pptx"
    with ZipFile(pptx, "w") as z:
        z.writestr("ppt/media/image2.png", first)
        z.writestr("ppt/media/image3.png", second)
    dest = tmp_path / "out"
    produced = extractor.extract(pptx, dest)
    assert [p.name for p in produced] == ["title.png", "sld.png"]
    assert [p.read_bytes() for p in produced] == [first, second]


def test_wrong_source_rejected_without_half_written_pngs(tmp_path, monkeypatch):
    monkeypatch.setattr(extractor, "EXPECTED", {
        "ppt/media/image2.png": ("title.png", hashlib.sha256(b"expected").hexdigest()),
        "ppt/media/image3.png": ("sld.png", hashlib.sha256(b"expected").hexdigest()),
    })
    pptx = tmp_path / "wrong.pptx"
    with ZipFile(pptx, "w") as z:
        z.writestr("ppt/media/image2.png", b"bad")
        z.writestr("ppt/media/image3.png", b"bad")
    target = tmp_path / "recovered"
    with pytest.raises(ValueError, match="differs"):
        extractor.extract(pptx, target)
    assert not target.exists()


def test_invalid_archive_is_not_treated_as_original(tmp_path):
    file = tmp_path / "invalid.pptx"
    file.write_text("not a PPTX", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid"):
        extractor.extract(file, tmp_path / "out")
