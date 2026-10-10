"""Public demo is synthetic-only at SERVER rendering, not merely a CSS hidden control."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MARKER = "PUBLIC SYNTHETIC DEMO"


def test_public_main_app_cannot_upload_images_or_trigger_vertex(monkeypatch):
    monkeypatch.setenv("HELIOPOLIS_DEMO_ONLY", "1")
    app = AppTest.from_file(ROOT / "app.py", default_timeout=60).run()
    assert not app.exception
    visible = " ".join(
        str(x.value) for x in (*app.info, *app.warning, *app.markdown)
    )
    assert PUBLIC_MARKER in visible
    # Uploaded-document controls must be removed from the actual widget tree.
    assert not app.get("file_uploader")
    assert not any("authorization to send" in x.label for x in app.checkbox)


def test_public_demo_keeps_maic_source_preset_and_review_warning(monkeypatch):
    monkeypatch.setenv("HELIOPOLIS_DEMO_ONLY", "1")
    app = AppTest.from_file(ROOT / "app.py", default_timeout=60).run()
    assert not app.exception
    preset = next(x for x in app.selectbox if x.label == "Load Site Preset")
    preset.set_value("MAIC 2026 Source Title (2-acre SYNTHETIC)").run()
    assert not app.exception
    assert any("NEEDS_REVIEW" in str(x.value) for x in app.error)
    assert not app.get("file_uploader")


def test_public_solar_atap_page_is_synthetic_no_customer_csv(monkeypatch):
    monkeypatch.setenv("HELIOPOLIS_DEMO_ONLY", "1")
    app = AppTest.from_file(
        ROOT / "pages" / "1_Solar_ATAP_Monthly.py", default_timeout=60
    ).run()
    assert not app.exception
    assert any(PUBLIC_MARKER in str(x.value) for x in app.info)
    assert not app.get("file_uploader")
    assert not any(x.label == "Evidence mode" for x in app.radio)
    assert any("Calculate energy-only" in x.label for x in app.button)
