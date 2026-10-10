"""Local OCR smoke command tests: never call a real provider or expose owner identifiers."""

from types import SimpleNamespace
import json

import networkx as nx
import pytest

import verify_live_ocr
from solar_agent import DocumentReviewRequired


def test_real_doc_transmission_requires_explicit_permission(tmp_path, monkeypatch):
    file = tmp_path / "private.png"
    file.write_bytes(b"fake-png-unit-test")
    monkeypatch.setenv("GEMINI_API_KEY", "placeholder-test-value")
    with pytest.raises(PermissionError, match="permission"):
        verify_live_ocr.verify_document(file, "TITLE")


def test_no_cloud_credentials_never_attempts_document_ocr(tmp_path, monkeypatch):
    file = tmp_path / "private.png"
    file.write_bytes(b"fake-png-unit-test")
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_CLOUD_PROJECT"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="No Gemini"):
        verify_live_ocr.verify_document(
            file, "TITLE", confirm_cloud_processing=True
        )


def test_sanitized_title_audit_excludes_names_and_ids(tmp_path, monkeypatch):
    file = tmp_path / "private-person-name.png"
    file.write_bytes(b"fake-png-unit-test")
    monkeypatch.setenv("GEMINI_API_KEY", "unit-test-no-network")
    meta = SimpleNamespace(
        owners=[SimpleNamespace(name="VERY PRIVATE NAME", ic_or_co_no="PRIVATE-ID")],
        area_sq_meters=4000.0,
        review_status="NEEDS_LEGAL_REVIEW",
    )
    monkeypatch.setattr(verify_live_ocr.LandTitleParser, "from_image", lambda _: meta)
    result = verify_live_ocr.verify_document(file, "TITLE", confirm_cloud_processing=True)
    assert result["status"] == "STRUCTURED_EXTRACTION_NEEDS_HUMAN_CHECK"
    assert result["field_level_accuracy"] is None
    content = json.dumps(result)
    assert "VERY PRIVATE NAME" not in content
    assert "PRIVATE-ID" not in content
    assert "private-person-name" not in content
    assert result["document_sha256"]


def test_mock_sld_smoke_never_implies_grid_approval(tmp_path, monkeypatch):
    file = tmp_path / "sld.png"
    file.write_bytes(b"fake-png-unit-test")
    monkeypatch.setenv("GEMINI_API_KEY", "unit-test-no-network")
    graph = nx.DiGraph()
    graph.add_nodes_from(["pv", "inverter"])
    graph.graph["tnb_compliance"] = {"preliminary_topology_status": "NEEDS_REVIEW"}
    monkeypatch.setattr(verify_live_ocr.SLDTopologyResolver, "resolve_image", lambda self, path: graph)
    result = verify_live_ocr.verify_document(file, "SLD", confirm_cloud_processing=True)
    assert result["status"] == "TOPOLOGY_EXTRACTED_NEEDS_HUMAN_CHECK"
    assert result["modeled_topology_status"] == "NEEDS_REVIEW"
    assert result["no_legal_or_grid_approval"] is True


def test_ocr_error_is_review_not_fabricated_approval(tmp_path, monkeypatch):
    file = tmp_path / "bad.png"
    file.write_bytes(b"fake-png-unit-test")
    monkeypatch.setenv("GEMINI_API_KEY", "unit-test-no-network")
    def reject(_):
        raise DocumentReviewRequired("critical title fields unreadable")
    monkeypatch.setattr(verify_live_ocr.LandTitleParser, "from_image", reject)
    result = verify_live_ocr.verify_document(file, "TITLE", confirm_cloud_processing=True)
    assert result["status"] == "NEEDS_REVIEW"
    assert "unreadable" in result["review_reason"]
