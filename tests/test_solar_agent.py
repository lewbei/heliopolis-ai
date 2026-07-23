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
    YieldFeasibilityEngine
)

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
    """
    Verifies that local substation capacity audits correctly trigger
    Battery Energy Storage (BESS) sizing above the 15% thermal threshold.
    """
    # Case 1: Peak AC is 1.0 MW, Substation is 10.0 MVA (10% injection, below 15%)
    safe_audit = TNBSubstationCapacityValidator.audit_injection(proposed_ac_mw=1.0, upstream_substation_mva=10.0)
    assert not safe_audit.bess_specification.is_bess_required
    
    # Case 2: Peak AC is 3.21 MW, Substation is 10.0 MVA (32.1% injection, above 15%)
    bess_audit = TNBSubstationCapacityValidator.audit_injection(proposed_ac_mw=3.21, upstream_substation_mva=10.0)
    assert bess_audit.bess_specification.is_bess_required
    assert bess_audit.bess_specification.recommended_battery_power_mw == 1.71
    assert bess_audit.bess_specification.recommended_battery_capacity_mwh == 6.84
    assert bess_audit.bess_specification.estimated_bess_capex_rm == 8208000.0


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
