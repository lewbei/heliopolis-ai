"""Streamlit MAIC live-demo finance consistency, after P0 #17 repair.

No Vertex credentials, uploads, actual title ownership, or Cloud Run are used.
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1] / "app.py"


def _html(at):
    return " ".join(str(item.value) for item in at.markdown)


def test_widget_ac_capacity_drives_rendered_dc_peak_without_changing_source_land():
    app = AppTest.from_file(ROOT, default_timeout=60).run()
    assert not app.exception
    before = _html(app)
    assert "3.776 MWp" in before, "Expected DC MWp = 3.21/0.85"
    ac = next(x for x in app.number_input if x.label == "Proposed AC Capacity (MWac)")
    ac.set_value(2.0).run()
    assert not app.exception
    after = _html(app)
    assert "2.353 MWp" in after, "Expected DC MWp = 2.00/0.85"
    assert "3.776 MWp" not in after
    assert "Estimated land required" in " ".join(str(x.label) for x in app.metric)


def test_two_acre_pitch_input_surfaces_review_without_fake_roi():
    app = AppTest.from_file(ROOT, default_timeout=60).run()
    assert not app.exception
    acres = next(x for x in app.number_input if x.label == "Ekar (Acres)")
    acres.set_value(2.0).run()
    assert not app.exception
    roods = next(x for x in app.number_input if x.label == "Rood")
    roods.set_value(0.0).run()
    assert not app.exception
    poles = next(x for x in app.number_input if x.label == "Pole")
    poles.set_value(0.0).run()
    assert not app.exception
    warnings = " ".join(str(w.message) if hasattr(w, "message") else str(w.value) for w in app.error)
    assert "NEEDS_REVIEW" in warnings
    assert "land-footprint" in warnings or "LAND-AREA MISMATCH" in warnings
    html = _html(app)
    assert "Not estimated" in html
