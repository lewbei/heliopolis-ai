"""Streamlit integration check: synthetic example is separate and prominently labeled."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

PAGE = Path(__file__).resolve().parents[1] / "pages" / "1_Solar_ATAP_Monthly.py"


def test_atap_page_starts_without_api_key_or_real_data():
    app = AppTest.from_file(PAGE, default_timeout=45).run()
    assert not app.exception
    all_text = " ".join(str(x.value) for x in app.markdown)
    assert "Solar ATAP" in " ".join(str(x.value) for x in app.title) + all_text
    assert len(app.radio) >= 1


def test_atap_page_requires_explicit_demo_mode_for_filled_values():
    at = AppTest.from_file(PAGE, default_timeout=45).run()
    assert not at.exception
    assert at.radio[0].value.startswith("Manual billing totals")
    at.radio[0].set_value("Clearly synthetic MAIC judge fixture").run()
    assert not at.exception
    submit = [b for b in at.button if "Calculate energy-only" in b.label]
    assert len(submit) == 1
    submit[0].click().run()
    assert not at.exception
    assert any("Creditable export quantity" in m.label for m in at.metric)
    assert any("2,293.20" in str(m.value) for m in at.metric)
    md = " ".join(str(x.value) for x in at.markdown)
    assert "SYNTHETIC" in md or any("SYNTHETIC" in str(x.message) for x in at.warning)
