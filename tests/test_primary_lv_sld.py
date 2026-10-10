"""TNB Appendix B LV drawing checks; synthetic tests, NOT grid certification.

LV drawn PV -> inverter -> AC meter/grid need not show a separate external
relay or transformer. Inverter anti-islanding capability still needs evidence
and independent verification.
"""

from unittest.mock import patch

import networkx as nx
import pytest

from app_logic import build_demo_sld
from solar_agent import DocumentReviewRequired, SLDTopologyResolver


def lv_graph(*, annotated=False, text="", connected=True):
    g = nx.DiGraph()
    g.add_node("pv", category="PV_Array")
    g.add_node(
        "inv", category="Inverter",
        integrated_anti_islanding_label=annotated,
        anti_islanding_source_text=text,
    )
    g.add_node("grid", category="Grid_Connection")
    g.add_edge("pv", "inv")
    if connected:
        g.add_edge("inv", "grid")
    return g


def screen(g):
    return SLDTopologyResolver().validate_tnb_compliance(g, connection_profile="LV")


def test_lv_tnb_style_drawing_does_not_require_separate_relay_or_transformer():
    """The topology exists; missing *inverter* evidence is a review task, not missing MV gear."""
    r = screen(lv_graph())
    assert r["connection_profile"] == "LV"
    assert r["transformer_count"] == 0
    assert r["anti_islanding_relay_present"] is False
    assert r["grid_path_valid"] is False
    assert r["preliminary_topology_status"] == "NEEDS_REVIEW"
    assert any("Anti-islanding evidence not visible" in f for f in r["findings"])
    assert not any("Missing modeled component: transformer" in f for f in r["findings"])
    assert not any("Missing modeled component: anti-islanding relay" in f for f in r["findings"])


def test_explicit_lv_inverter_label_allows_bounded_preliminary_topology_screen():
    r = screen(lv_graph(annotated=True, text="Anti-islanding inverter IEC 62116"))
    assert r["preliminary_topology_status"] == "PRELIMINARY_TOPOLOGY_PASS"
    assert r["grid_path_valid"]
    assert r["integrated_anti_islanding_label_visible"] is True
    assert "not a tnb approval" in r["scope_note"].lower()
    assert "independent verification" in r["scope_note"].lower()


@pytest.mark.parametrize("label, text", [
    (None, "anti-islanding"),
    (False, "Anti-islanding inverter"),
    (True, ""),
    (True, "ordinary grid-tie inverter"),
    (True, "no anti-islanding provided"),
])
def test_labeled_vs_inferred_protection_cannot_silently_pass(label, text):
    r = screen(lv_graph(annotated=label, text=text))
    assert r["preliminary_topology_status"] == "NEEDS_REVIEW"


def test_explicit_relay_inline_can_support_lv_evidence_even_without_inverter_label():
    g = lv_graph()
    g.remove_edge("inv", "grid")
    g.add_node("relay", category="Anti_Islanding_Relay")
    g.add_edges_from([("inv", "relay"), ("relay", "grid")])
    r = screen(g)
    assert r["grid_path_valid"]
    assert r["anti_islanding_relay_present"] is True


def test_unconnected_lv_inverter_is_review_required():
    r = screen(lv_graph(annotated=True, text="Anti-islanding", connected=False))
    assert not r["grid_path_valid"]
    assert any("No complete modeled" in f for f in r["findings"])


def test_reversed_pv_inverter_connection_is_not_a_path():
    g = lv_graph(annotated=True, text="Anti-islanding")
    g.remove_edge("pv", "inv")
    g.add_edge("inv", "pv")
    assert screen(g)["preliminary_topology_status"] == "NEEDS_REVIEW"


def test_direct_pv_to_grid_bypass_fails_even_when_protected_path_exists():
    g = lv_graph(annotated=True, text="IEC 62116")
    g.add_edge("pv", "grid")
    r = screen(g)
    assert not r["grid_path_valid"]
    assert any("bypassing all modeled inverters" in f for f in r["findings"])


def test_second_unprotected_inverter_path_prevents_false_clearance():
    g = lv_graph(annotated=True, text="Anti-islanding")
    g.add_node("bad_inv", category="Inverter", integrated_anti_islanding_label=False)
    g.add_edges_from([("pv", "bad_inv"), ("bad_inv", "grid")])
    r = screen(g)
    assert not r["grid_path_valid"]
    assert any("bypassing displayed anti-islanding protection" in f for f in r["findings"])


def test_lv_requires_inverter_and_grid_nodes():
    g = lv_graph()
    g.remove_node("inv")
    r = screen(g)
    assert r["preliminary_topology_status"] == "NEEDS_REVIEW"
    assert "Missing modeled component: inverter" in r["findings"]


def test_mv_profile_is_not_loosened_by_lv_mode():
    g = lv_graph(annotated=True, text="IEC 62116")
    mv = SLDTopologyResolver().validate_tnb_compliance(g)
    assert mv["connection_profile"] == "MV"
    assert mv["preliminary_topology_status"] == "NEEDS_REVIEW"
    assert "Missing modeled component: transformer" in mv["findings"]
    assert "Missing modeled component: anti-islanding relay" in mv["findings"]


@pytest.mark.parametrize("profile", ["UNKNOWN", "HV", ""])
def test_unknown_or_hv_profile_does_not_become_compliant(profile):
    g = lv_graph(annotated=True, text="Anti-islanding")
    r = SLDTopologyResolver().validate_tnb_compliance(g, connection_profile=profile)
    assert not r["grid_path_valid"]
    assert r["preliminary_topology_status"] == "NEEDS_REVIEW"
    assert "No validated SLD topology profile" in r["findings"][0]


@pytest.mark.parametrize("label,connected,expected", [
    (True, True, "PRELIMINARY_TOPOLOGY_PASS"),
    (False, True, "NEEDS_REVIEW"),
    (True, False, "NEEDS_REVIEW"),
])
def test_offline_primary_lv_fixture_negative_controls(label, connected, expected):
    g = build_demo_sld(
        has_relay=label, is_xfmr_connected=connected, connection_profile="LV"
    )
    assert g.graph["source_type"] == "SYNTHETIC_DEMO"
    assert g.graph["tnb_compliance"]["preliminary_topology_status"] == expected
    assert g.graph["tnb_compliance"]["connection_profile"] == "LV"
    assert len([n for n, d in g.nodes(data=True) if d["category"] == "Transformer"]) == 0


def test_uploaded_lv_ocr_keeps_source_and_fails_safe_on_absent_label():
    symbols = [
        {"id": "pv", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
        {"id": "inv", "class": "Inverter", "bbox": [100, 400, 200, 500]},
        {"id": "grid", "class": "Grid_Connection", "bbox": [100, 700, 200, 800]},
    ]
    data = {
        "symbols": symbols,
        "lines": [
            ((200, 150), (400, 150)),
            ((500, 150), (700, 150)),
        ],
    }
    with patch("solar_agent.heliopolis_ocr.parse_sld_image", return_value=data):
        g = SLDTopologyResolver().resolve_image(
            "permitted-lv-drawing.png", connection_profile="LV"
        )
    assert g.graph["source_type"] == "OCR_EXTRACTED_UNVERIFIED"
    assert g.graph["tnb_compliance"]["preliminary_topology_status"] == "NEEDS_REVIEW"
    assert g.graph["connection_profile"] == "LV"


def test_uploaded_lv_label_requires_actual_short_text_not_truthy_string():
    data = {
        "symbols": [
            {"id": "pv", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
            {
                "id": "inv", "class": "Inverter", "bbox": [100, 400, 200, 500],
                "integrated_anti_islanding_label": "true",
                "anti_islanding_source_text": "anti-islanding",
            },
            {"id": "grid", "class": "Grid_Connection", "bbox": [100, 700, 200, 800]},
        ],
        "lines": [((200, 150), (400, 150)), ((500, 150), (700, 150))],
    }
    with patch("solar_agent.heliopolis_ocr.parse_sld_image", return_value=data):
        with pytest.raises(DocumentReviewRequired):
            SLDTopologyResolver().resolve_image(
                "permitted-lv.png", connection_profile="LV"
            )


def test_uploaded_lv_explicit_label_is_still_preliminary():
    data = {
        "symbols": [
            {"id": "pv", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
            {
                "id": "inv", "class": "Inverter", "bbox": [100, 400, 200, 500],
                "integrated_anti_islanding_label": True,
                "anti_islanding_source_text": "Anti-islanding inverter",
            },
            {"id": "grid", "class": "Grid_Connection", "bbox": [100, 700, 200, 800]},
        ],
        "lines": [((200, 150), (400, 150)), ((500, 150), (700, 150))],
    }
    with patch("solar_agent.heliopolis_ocr.parse_sld_image", return_value=data):
        g = SLDTopologyResolver().resolve_image(
            "permitted-lv.png", connection_profile="LV"
        )
    r = g.graph["tnb_compliance"]
    assert r["preliminary_topology_status"] == "PRELIMINARY_TOPOLOGY_PASS"
    assert "Not a TNB approval" in r["scope_note"]
    assert g.graph["source_type"] == "OCR_EXTRACTED_UNVERIFIED"



def test_tnb_appendix_b_lv_route_with_switch_and_pv_meter_is_not_mv_path():
    """The drawn AC switch/meter may occur between inverter and LV grid terminals."""
    g = lv_graph(annotated=True, text="Anti-islanding grid inverter")
    g.remove_edge("inv", "grid")
    g.add_node("switch", category="AC_Switch")
    g.add_node("pv_meter", category="PV_Meter")
    g.add_edges_from([
        ("inv", "switch"),
        ("switch", "pv_meter"),
        ("pv_meter", "grid"),
    ])
    lv = screen(g)
    assert lv["preliminary_topology_status"] == "PRELIMINARY_TOPOLOGY_PASS"
    assert lv["transformer_count"] == 0
    mv = SLDTopologyResolver().validate_tnb_compliance(g, connection_profile="MV")
    assert mv["preliminary_topology_status"] == "NEEDS_REVIEW"
