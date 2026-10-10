"""Offline Streamlit smoke tests for unsupported consumer offset finance modes."""

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize("keyword", ["Historical NOVA", "Self-consumption"])
def test_missing_load_profile_disables_profitability_without_crashing(keyword):
    app = AppTest.from_file("app.py", default_timeout=60).run()
    assert not app.exception
    choices = [widget for widget in app.selectbox if widget.label == "Revenue Scenario"]
    assert len(choices) == 1
    select = choices[0]
    candidates = [value for value in select.options if keyword.lower() in str(value).lower()]
    assert len(candidates) == 1, f"Could not find {keyword} among {select.options}"
    app = select.set_value(candidates[0]).run()
    assert not app.exception
    # This is only a smoke check. The backend numerical abstention is verified
    # in test_regulatory_fail_closed.py.
    markdown = " ".join(str(x.value) for x in app.markdown)
    assert "Not estimated" in markdown or "withheld" in markdown
