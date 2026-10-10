from types import SimpleNamespace

from app_components import owner_rows_html


def test_ocr_owner_content_cannot_inject_html():
    owner = SimpleNamespace(
        name="<img src=x onerror=alert(1)>",
        ic_or_co_no="A&B",
        share_fraction="<b>1/1</b>",
        calculated_share_float=1.0,
    )
    html = owner_rows_html([owner])
    assert "<img" not in html and "onerror=" in html
    assert "&lt;img" in html and "A&amp;B" in html
    assert "&lt;b&gt;1/1&lt;/b&gt;" in html
