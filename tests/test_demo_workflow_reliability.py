"""End-to-end synthetic UI/export checks; no credentials or network model calls."""
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import heliopolis_ocr

ROOT = Path(__file__).resolve().parents[1]
PRESET = "MAIC 2026 Source Title (2-acre SYNTHETIC)"


@pytest.fixture
def offline_app(monkeypatch):
    monkeypatch.setenv("HELIOPOLIS_DEMO_ONLY", "1")
    for name in ("parse_land_title_image", "parse_sld_image"):
        monkeypatch.setattr(heliopolis_ocr, name, Mock(side_effect=AssertionError("Offline demo invoked OCR")))
    reports = {}
    original = st.download_button

    def capture(*args, **kwargs):
        if kwargs.get("mime") == "application/json":
            reports[kwargs["file_name"]] = json.loads(kwargs["data"])
        return original(*args, **kwargs)

    monkeypatch.setattr(st, "download_button", capture)
    app = AppTest.from_file(ROOT / "app.py", default_timeout=60).run()
    assert not app.exception
    yield app, reports
    heliopolis_ocr.parse_land_title_image.assert_not_called()
    heliopolis_ocr.parse_sld_image.assert_not_called()


def widget(app, kind, label):
    return next(w for w in getattr(app, kind) if w.label == label)


def test_source_capacity_edit_export_and_restart_are_consistent(offline_app):
    app, reports = offline_app
    widget(app, "selectbox", "Load Site Preset").set_value(PRESET).run()
    report = reports["solar_assessment_report.json"]
    assert report["land_title_analysis"]["title_no"] == "SYNTH-GRN-2026-001"
    assert report["land_title_analysis"]["area_sq_meters"] == pytest.approx(8093.7128, abs=.1)
    assert report["financial_feasibility"]["proposed_ac_mw"] == 3.21
    assert report["sld_topology_screen"]["preliminary_topology_status"] == "NEEDS_REVIEW"
    widget(app, "number_input", "Proposed AC Capacity (MWac)").set_value(2.0).run()
    report = reports["solar_assessment_report.json"]
    assert not app.exception
    assert report["financial_feasibility"]["capacity_mwp"] == pytest.approx(2 / .85, abs=.001)
    assert report["financial_feasibility"]["project_npv_rm"] is None
    assert report["regulatory_planning_fields"]["seda"]["Part_C_Proposed_AC_Capacity_kWac"] == 2000
    assert report["assessment_status"] == "NEEDS_REVIEW"
    assert report["ocr_status"]["title"] == report["ocr_status"]["sld"] == "NOT_USED"
    assert not app.get("file_uploader")
    app.run()
    assert reports["solar_assessment_report.json"] == report
    fresh = AppTest.from_file(ROOT / "app.py", default_timeout=60).run()
    widget(fresh, "selectbox", "Load Site Preset").set_value(PRESET).run()
    assert not fresh.exception
    assert reports["solar_assessment_report.json"]["financial_feasibility"]["proposed_ac_mw"] == 3.21


def test_modified_source_and_preset_switch_clear_old_provenance(offline_app):
    app, reports = offline_app
    widget(app, "selectbox", "Load Site Preset").set_value(PRESET).run()
    widget(app, "number_input", "Ekar (Acres)").set_value(25.0).run()
    report = reports["solar_assessment_report.json"]
    assert report["data_provenance"]["title_fields_modified_from_pitched_source"] is True
    assert report["land_title_analysis"]["source_type"] == "USER_EDITED_SYNTHETIC_PITCH_FIELDS"
    picker = widget(app, "selectbox", "Load Site Preset")
    picker.set_value(next(s for s in picker.options if s != PRESET)).run()
    report = reports["solar_assessment_report.json"]
    assert not app.exception
    assert report["data_provenance"]["source_case_id"] is None
    assert report["data_provenance"]["title_original_sha256"] is None
    assert report["data_provenance"]["sld_original_sha256"] is None
    assert report["land_title_analysis"]["title_no"] != "SYNTH-GRN-2026-001"


def test_graph_negative_control_export_and_repeated_toggle_match(offline_app):
    app, reports = offline_app
    widget(app, "selectbox", "Connection voltage class (user assumption)").set_value("MV").run()
    for connected in (False, True, False):
        widget(app, "toggle", "Connect Transformer to Grid (synthetic)").set_value(connected).run()
        assert not app.exception
        report = reports["solar_assessment_report.json"]
        screen = report["sld_topology_screen"]
        assert screen["grid_path_valid"] is connected
        assert screen["preliminary_topology_status"] == ("PRELIMINARY_TOPOLOGY_PASS" if connected else "NEEDS_REVIEW")
        if not connected:
            assert any("NEEDS REVIEW" in str(x.value) for x in app.error)
    widget(app, "number_input", "Proposed AC Capacity (MWac)").set_value(-1.0).run()
    assert not app.exception
    assert app.error
    assert not app.get("download_button"), "Invalid new input must remove the previous successful export"
