import os
import sys
import numpy as np
import networkx as nx
import pytest

# Ensure our local path is in sys.path to import solar_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solar_agent import (
    LandTitleParser,
    CivilSlopeAnalyzer,
    TNBSubstationCapacityValidator,
    SLDTopologyResolver,
    YieldFeasibilityEngine,
    FormFiller,
    SCENARIO_C_I_NEM,
    DocumentReviewRequired,
)
from unittest.mock import patch

# Shared SLD fixture used by the resolver test (kept in one place).
SAMPLE_SLD_SYMBOLS = [
    {"id": "PV_1", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
    {"id": "INV_1", "class": "Inverter", "bbox": [100, 400, 200, 500]},
    {"id": "RELAY_1", "class": "Anti_Islanding_Relay", "bbox": [100, 700, 200, 800]},
    {"id": "XFMR_1", "class": "Transformer", "bbox": [100, 1000, 200, 1100]},
    {"id": "GRID_1", "class": "Grid_Connection", "bbox": [100, 1300, 200, 1400]}
]

SAMPLE_SLD_LINES = [
    ((200, 150), (400, 150)),
    ((500, 150), (700, 150)),
    ((800, 150), (1000, 150)),
    ((1100, 150), (1300, 150))
]

def test_imperial_conversions():
    """
    Verifies that the imperial-to-metric converter correctly transforms
    Ekar (Acres), Rood, and Pole units into precise hectares and square meters.
    """
    # 12 Acres, 2 Roods, 15 Poles
    hectares, sq_meters = LandTitleParser.convert_imperial_to_metric(acres=12.0, roods=2.0, poles=15.0)
    
    assert hectares == 5.0965
    assert sq_meters == pytest.approx(50965.1, rel=1e-4)

def test_fraction_parsing():
    """
    Verifies fractional parsing math for fragmented tenancy shares.
    """
    parser = LandTitleParser()
    assert parser.parse_fraction("11/120") == pytest.approx(0.0916666, rel=1e-5)
    assert parser.parse_fraction("Semua") == 1.0
    assert parser.parse_fraction("1/1") == 1.0
    assert parser.parse_fraction("Invalid") == 0.0

def test_slope_grading_premiums():
    """
    Verifies that 2D spatial elevation gradients are calculated correctly
    and trigger the 35% civil grading cost premium on slopes > 30 degrees.
    """
    # Create a 2D flat grid
    flat_grid = np.zeros((5, 5))
    flat_profile = CivilSlopeAnalyzer.analyze_topography(flat_grid, cell_resolution_meters=10.0)
    assert flat_profile.mean_slope_degrees == 0.0
    assert flat_profile.grading_capex_premium_multiplier == 1.0
    
    # Create a steep sloped grid (exceeding 30 degrees)
    y, x = np.mgrid[0:50:10, 0:50:10]
    steep_grid = x * 10.0 # Extreme elevation step (10m per cell)
    steep_profile = CivilSlopeAnalyzer.analyze_topography(steep_grid, cell_resolution_meters=10.0)
    assert steep_profile.mean_slope_degrees == pytest.approx(84.29, abs=0.1)
    assert steep_profile.landslide_risk == "High (Unbuildable / Severe Slope)"
    assert steep_profile.grading_capex_premium_multiplier == 1.35

def test_sld_topology_resolver():
    """
    Verifies that coordinate epsilon-proximity matching correctly connects nodes,
    and programmatically detects TNB grid code compliance.
    """
    resolver = SLDTopologyResolver()
    g = resolver.resolve(SAMPLE_SLD_SYMBOLS, SAMPLE_SLD_LINES)

    assert g.number_of_nodes() == 5
    assert g.number_of_edges() == 4
    assert nx.has_path(g, "XFMR_1", "GRID_1")

    # TNB compliance metadata should be attached to the graph.
    compliance = g.graph.get("tnb_compliance", {})
    assert compliance.get("anti_islanding_relay_present") is True
    assert compliance.get("grid_path_valid") is True

def test_bess_sizing_triggers():
    """The 15% MW/MVA heuristic does NOT establish a TNB-mandated BESS requirement."""
    # Case 1: Peak AC is 1.0 MW, Substation is 10.0 MVA (10% injection, below 15%)
    safe_audit = TNBSubstationCapacityValidator.audit_injection(proposed_ac_mw=1.0, upstream_substation_mva=10.0)
    assert not safe_audit.bess_specification.is_bess_required
    
    # Case 2: Peak AC is 3.21 MW, Substation is 10.0 MVA (32.1% injection, above 15%)
    bess_audit = TNBSubstationCapacityValidator.audit_injection(proposed_ac_mw=3.21, upstream_substation_mva=10.0)
    assert not bess_audit.bess_specification.is_bess_required
    assert bess_audit.reverse_power_risk == "SCREENING_FLAG_NEEDS_UTILITY_STUDY"
    assert bess_audit.bess_specification.recommended_battery_capacity_mwh == 0.0

    # Explicit hypothetical BESS sizing is permitted, but is not labeled mandatory.
    optional = TNBSubstationCapacityValidator.audit_injection(3.21, 10.0, hypothetical_bess=True)
    assert not optional.bess_specification.is_bess_required
    assert optional.bess_specification.recommended_battery_power_mw == 1.71
    assert optional.bess_specification.recommended_battery_capacity_mwh == 6.84
    assert optional.bess_specification.estimated_bess_capex_rm == 8208000.0


def test_sld_junction_dot_connects_branch():
    """
    A main bus (PV -> Inverter -> Transformer) with a branch line from the
    inverter to a Load should only connect when a junction dot is present at
    the branch point.
    """
    symbols = [
        {"id": "PV_1", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
        {"id": "INV_1", "class": "Inverter", "bbox": [100, 400, 200, 500]},
        {"id": "XFMR_1", "class": "Transformer", "bbox": [100, 700, 200, 800]},
        {"id": "LOAD_1", "class": "Grid_Connection", "bbox": [400, 400, 500, 500]},
    ]
    # Main horizontal line through the inverter bbox; branch goes down from the junction dot.
    main_line = ((200, 150), (700, 150))  # PV to Transformer, passes through INV_1
    branch_line = ((450, 150), (450, 400))  # from junction dot down to LOAD_1
    junction_dots = [(450, 150)]

    resolver = SLDTopologyResolver()
    g = resolver.resolve(symbols, [main_line, branch_line], junction_dots=junction_dots)

    # The junction dot splits the main line and connects the branch.
    assert nx.has_path(g, "PV_1", "XFMR_1")
    assert nx.has_path(g, "INV_1", "LOAD_1")
    # The branch must route through the virtual junction node.
    assert any("JUNCTION" in n for n in g.nodes())


def test_sld_crossing_without_junction_dot_is_not_connected():
    """
    Two independent circuits that cross geometrically without a junction dot
    must remain separate networks.
    """
    symbols = [
        {"id": "PV_1", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
        {"id": "INV_1", "class": "Inverter", "bbox": [100, 400, 200, 500]},
        {"id": "PV_2", "class": "PV_Array", "bbox": [400, 100, 500, 200]},
        {"id": "INV_2", "class": "Inverter", "bbox": [400, 400, 500, 500]},
    ]
    # Two independent vertical lines that happen to cross the same horizontal line
    # at (300, 150) without a junction dot.
    lines = [
        ((200, 150), (400, 150)),  # horizontal crossing line (PV1 side to PV2 side)
        ((300, 150), (300, 450)),  # vertical line from PV2 to INV2 passing through crossing
    ]

    resolver = SLDTopologyResolver()
    g = resolver.resolve(symbols, lines, junction_dots=[])

    # Without a junction dot, the horizontal line only connects if its endpoints
    # fall inside symbol bboxes. Here (200,150) is near PV_1 but (400,150) is near
    # PV_2 only in y, not x; it will not connect to PV_2. The vertical line
    # endpoints (300,150) and (300,450) have no nearby symbols. Therefore no
    # spurious connection between the two circuits should be created.
    assert g.number_of_edges() == 0 or not nx.has_path(g, "PV_1", "INV_2")


# Adversarial reliability tests: malformed inputs must not quietly become
# synthetic approvals. These fixtures test engineering logic, NOT field accuracy.
def _valid_title_extraction():
    return {
        "title_no": "GRN 100", "lot_no": "Lot 10", "state": "Kedah",
        "district": "Kubang Pasu", "mukim": "A", "zoning": "Bangunan",
        "area_acres": 1.0, "area_roods": 0.0, "area_poles": 0.0,
        "has_caveats": False, "has_charges": False, "is_malay_reserve": False,
        "owners": [{"name": "Test Owner", "ic_or_co_no": "TEST-1", "share_fraction": "1/1"}],
    }


@pytest.mark.parametrize("extracted", [None, {}, {"title_no": "GRN 100"}])
def test_uploaded_title_does_not_fallback_to_demo(extracted):
    with patch("solar_agent.heliopolis_ocr.parse_land_title_image", return_value=extracted):
        with pytest.raises(DocumentReviewRequired):
            LandTitleParser.from_image("a-malformed-upload.png")


@pytest.mark.parametrize("key,value", [
    ("has_caveats", None), ("has_charges", None), ("is_malay_reserve", None),
    ("area_acres", None), ("area_roods", 4.0),
    ("owners", []),
    ("owners", [{"name": "Test", "ic_or_co_no": "1", "share_fraction": "1/2"}]),
])
def test_uploaded_title_unknown_restrictions_and_inconsistent_fields_require_review(key, value):
    extracted = _valid_title_extraction()
    extracted[key] = value
    with patch("solar_agent.heliopolis_ocr.parse_land_title_image", return_value=extracted):
        with pytest.raises(DocumentReviewRequired):
            LandTitleParser.from_image("bad-title.png")


def test_valid_title_is_extracted_but_never_legally_approved():
    with patch("solar_agent.heliopolis_ocr.parse_land_title_image", return_value=_valid_title_extraction()):
        result = LandTitleParser.from_image("valid-title.png")
    assert result.title_no == "GRN 100"
    assert result.source_type == "OCR_EXTRACTED_UNVERIFIED"
    assert result.review_status == "NEEDS_LEGAL_REVIEW"
    assert result.legal_assessment.status != "Approved"


def test_uploaded_sld_does_not_fallback_to_compliant_fixture():
    with patch("solar_agent.heliopolis_ocr.parse_sld_image", return_value=None):
        with pytest.raises(DocumentReviewRequired):
            SLDTopologyResolver().resolve_image("bad-sld.png")
    with patch("solar_agent.heliopolis_ocr.parse_sld_image", return_value={"symbols": [], "lines": []}):
        with pytest.raises(DocumentReviewRequired):
            SLDTopologyResolver().resolve_image("empty-sld.png")


def test_disconnected_relay_cannot_pass_topology():
    lines = [
        SAMPLE_SLD_LINES[0],  # PV -> INV
        ((500, 150), (1000, 150)),  # INV -> transformer, bypass relay
        SAMPLE_SLD_LINES[3],  # transformer -> grid
    ]
    graph = SLDTopologyResolver().resolve(SAMPLE_SLD_SYMBOLS, lines)
    result = graph.graph["tnb_compliance"]
    assert result["anti_islanding_relay_present"] is True
    assert result["grid_path_valid"] is False
    assert result["preliminary_topology_status"] == "NEEDS_REVIEW"


def test_missing_relay_cannot_pass_topology():
    symbols = [s for s in SAMPLE_SLD_SYMBOLS if s["class"] != "Anti_Islanding_Relay"]
    graph = SLDTopologyResolver().resolve(symbols, [
        SAMPLE_SLD_LINES[0], ((500, 150), (1000, 150)), SAMPLE_SLD_LINES[3],
    ])
    assert graph.graph["tnb_compliance"]["grid_path_valid"] is False


def test_valid_topology_is_only_preliminary():
    result = SLDTopologyResolver().resolve(SAMPLE_SLD_SYMBOLS, SAMPLE_SLD_LINES).graph["tnb_compliance"]
    assert result["preliminary_topology_status"] == "PRELIMINARY_TOPOLOGY_PASS"
    assert "not a tnb" in result["scope_note"].lower()


@pytest.mark.parametrize("capacity_kw,study,fee", [
    (72.0, False, 0.0),
    (72.01, True, 1000.0),
    (180.0, True, 1000.0),
    (180.01, True, 5000.0),
    (425.0, True, 5000.0),
    (425.01, True, 8000.0),
    (1000.01, True, 15000.0),
    (5000.01, False, 0.0),
])
def test_nova_study_bands_are_scheme_specific(capacity_kw, study, fee):
    land = LandTitleParser().parse("")
    terrain = CivilSlopeAnalyzer.analyze_topography(np.zeros((5, 5)), 10.0)
    grid = TNBSubstationCapacityValidator.audit_injection(1.0, 10.0)
    tech = YieldFeasibilityEngine(land, terrain, grid).calculate(scenario=SCENARIO_C_I_NEM)
    manifest = FormFiller.generate_manifest(land, tech, proposed_ac_mw=capacity_kw / 1000.0, voltage_class="LV")
    assert manifest.nemas_checklist.is_nemas_required is study
    assert manifest.nemas_checklist.estimated_regulatory_fee_rm == (fee if study else None)
    assert manifest.seda_application.Part_C_Proposed_AC_Capacity_kWac == pytest.approx(capacity_kw)


def test_lss_does_not_inherit_nova_study_fee():
    land = LandTitleParser().parse("")
    terrain = CivilSlopeAnalyzer.analyze_topography(np.zeros((5, 5)), 10.0)
    grid = TNBSubstationCapacityValidator.audit_injection(3.0, 15.0)
    tech = YieldFeasibilityEngine(land, terrain, grid).calculate()
    m = FormFiller.generate_manifest(land, tech, proposed_ac_mw=3.0, voltage_class="MV")
    assert not m.nemas_checklist.is_nemas_required
    assert m.nemas_checklist.estimated_regulatory_fee_rm is None
    assert "not implemented" in " ".join(m.nemas_checklist.eligibility_notes).lower()
