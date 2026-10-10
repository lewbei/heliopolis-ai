"""The prepared source case is NOT the unrelated 12-acre site or a Vertex OCR run."""

from pathlib import Path
import networkx as nx

from streamlit.testing.v1 import AppTest

from app_logic import build_maic_pitch_source_sld, compute_assessment
from solar_agent import LandTitleParser, DocumentReviewRequired


ROOT = Path(__file__).resolve().parents[1] / "app.py"
PRESET = "MAIC 2026 Source Title (2-acre SYNTHETIC)"


def _select_source_app():
    app = AppTest.from_file(ROOT, default_timeout=60).run()
    assert not app.exception
    target = next(x for x in app.selectbox if x.label == "Load Site Preset")
    assert PRESET in target.options
    target.set_value(PRESET).run()
    assert not app.exception
    return app


def test_pitch_sld_main_power_route_is_not_false_protection_pass():
    graph = build_maic_pitch_source_sld()
    scope = graph.graph["tnb_compliance"]
    assert graph.graph["source_type"] == "SYNTHETIC_PITCH_SOURCE_REVIEWED_FIELDS"
    assert scope["connection_profile"] == "MV"
    assert scope["anti_islanding_relay_present"] is True
    assert scope["grid_path_valid"] is False
    assert scope["preliminary_topology_status"] == "NEEDS_REVIEW"
    assert nx.has_path(graph, "PV_1", "GRID_1")
    assert not nx.has_path(graph, "RELAY_AUX", "GRID_1")
    assert any("auxiliary" in note for note in scope["findings"])


def test_prepared_pitch_selected_case_loads_exact_title_and_review():
    app = _select_source_app()
    html = " ".join(str(x.value) for x in app.markdown)
    assert any("REVIEWED SYNTHETIC SOURCE FIELDS" in str(x.value) for x in app.warning)
    assert any("auxiliary sensing/control" in str(x.value) for x in app.error) or any(
        "auxiliary sensing/control" in str(x.value) for x in app.warning
    )
    assert any("2" in str(n.value) for n in app.number_input if n.label == "Ekar (Acres)")
    assert next(x for x in app.text_input if x.label == "Title No").value == "SYNTH-GRN-2026-001"
    assert next(x for x in app.text_input if x.label == "Lot No").value == "SYNTH-LOT-001"
    assert next(x for x in app.selectbox if x.label == "Connection voltage class (user assumption)").value == "MV"
    assert "SYNTHETIC PERSON ALPHA" in html
    assert "SYNTHETIC PERSON BETA" in html
    assert "NEEDS_REVIEW" in " ".join(str(x.value) for x in app.error)
    assert "Not estimated" in html
    assert not any("PRELIMINARY_TOPOLOGY_PASS" in str(x.value) for x in app.success)


def test_same_prepared_title_keeps_warning_after_2_mw_capacity_change():
    app = _select_source_app()
    ac = next(x for x in app.number_input if x.label == "Proposed AC Capacity (MWac)")
    assert ac.value == 3.21
    ac.set_value(2.0).run()
    assert not app.exception
    err = " ".join(str(x.value) for x in app.error)
    assert "NEEDS_REVIEW" in err
    assert "2.000 MWac exceeds" in err
    assert any("auxiliary" in str(x.value) for x in app.error) or any(
        "auxiliary" in str(x.value) for x in app.warning
    )
    assert "2.353 MWp" in " ".join(str(x.value) for x in app.markdown)
