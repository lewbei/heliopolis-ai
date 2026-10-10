"""Streamlit SLD negative controls: selected LV truly drives the exported graph view."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_primary_lv_ui_switches_profile_and_fails_on_missing_evidence():
    at = AppTest.from_file(APP_PATH, default_timeout=50).run()
    assert not at.exception
    picker = next(
        select for select in at.selectbox
        if select.label == "Connection voltage class (user assumption)"
    )
    picker.set_value("LV").run()
    assert not at.exception
    assert any("LV preliminary topology" in str(msg.value) for msg in at.success)
    assert any("Explicit inverter anti-islanding label" in t.label for t in at.toggle)

    label = next(
        toggle for toggle in at.toggle
        if "Explicit inverter anti-islanding label" in toggle.label
    )
    label.set_value(False).run()
    assert not at.exception
    assert any("Anti-islanding evidence not visible" in str(msg.value) for msg in at.error)


def test_unknown_connection_class_never_reports_preliminary_approval():
    at = AppTest.from_file(APP_PATH, default_timeout=50).run()
    assert not at.exception
    assert any(
        "No validated SLD topology profile" in str(msg.value)
        for msg in at.error
    )
