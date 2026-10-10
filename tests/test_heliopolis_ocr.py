import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

import heliopolis_ocr as ocr


def test_extract_json_plain():
    raw = json.dumps({"title_no": "GRN 12345", "state": "Perak"})
    assert ocr._extract_json(raw) == {"title_no": "GRN 12345", "state": "Perak"}


def test_extract_json_with_fences():
    raw = '```json\n{"title_no": "GRN 12345"}\n```'
    assert ocr._extract_json(raw) == {"title_no": "GRN 12345"}


def test_extract_json_invalid_returns_none():
    assert ocr._extract_json("not valid { json") is None


def test_extract_json_empty_returns_none():
    assert ocr._extract_json("") is None


def test_parse_land_title_image_success(tmp_path, monkeypatch):
    img_path = tmp_path / "title.png"
    Image.new("RGB", (64, 64), color="white").save(img_path)

    expected = {"title_no": "GRN 99999", "state": "Kedah"}
    with patch.object(ocr, "_generate_json", return_value=expected):
        result = ocr.parse_land_title_image(img_path)
    assert result == expected


def test_parse_land_title_image_missing_file():
    assert ocr.parse_land_title_image("/nonexistent/path.png") is None


def test_parse_sld_image_success(tmp_path, monkeypatch):
    img_path = tmp_path / "sld.png"
    Image.new("RGB", (64, 64), color="white").save(img_path)

    raw = {
        "symbols": [{"id": "PV_1", "class": "PV_Array", "bbox": [0, 0, 10, 10]}],
        "lines": [[[0, 0], [10, 10]]],
    }
    with patch.object(ocr, "_generate_json", return_value=raw):
        result = ocr.parse_sld_image(img_path)

    assert result["symbols"][0]["class"] == "PV_Array"
    assert result["lines"] == [((0.0, 0.0), (10.0, 10.0))]


def test_generate_json_falls_back_to_none_on_missing_credentials(monkeypatch):
    """When no credentials are present _generate_json returns None instead of crashing."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_LOCATION", raising=False)

    img = Image.new("RGB", (32, 32), color="white")
    assert ocr._generate_json("test prompt", img) is None


def test_generate_json_uses_client_when_available(monkeypatch):
    """When a client is available, parse the returned JSON response."""
    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.text = json.dumps({"title_no": "GRN 00001"})
    fake_client.models.generate_content.return_value = fake_response

    monkeypatch.setattr(ocr, "_get_client", lambda: (fake_client, "api_key"))

    img = Image.new("RGB", (32, 32), color="white")
    result = ocr._generate_json("test prompt", img)
    assert result == {"title_no": "GRN 00001"}
    fake_client.models.generate_content.assert_called_once()



@pytest.mark.parametrize("kind", ["title", "sld"])
def test_corrupted_uploaded_image_fails_closed_before_any_network_call(tmp_path, kind):
    fake = tmp_path / ("invalid-" + kind + ".png")
    fake.write_bytes(b"not a valid image, definitely not a legal document")
    with patch.object(ocr, "_generate_json", side_effect=AssertionError("Must not send an invalid image")):
        parsed = (
            ocr.parse_land_title_image(fake)
            if kind == "title" else ocr.parse_sld_image(fake)
        )
    assert parsed is None


def test_model_failure_logs_error_type_not_confidential_provider_response(capsys, monkeypatch):
    from PIL import Image
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError(
        "PRIVATE CUSTOMER TITLE CONTENT SHOULD NOT BE IN LOGS"
    )
    monkeypatch.setattr(ocr, "_get_client", lambda: (mock_client, "api_key"))
    image = Image.new("RGB", (8, 8), color="white")
    assert ocr._generate_json("test", image) is None
    log = capsys.readouterr().out
    assert "PRIVATE CUSTOMER TITLE" not in log
    assert "RuntimeError" in log
