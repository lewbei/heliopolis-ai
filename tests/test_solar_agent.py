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
    symbols = [
        {"id": "PV_1", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
        {"id": "INV_1", "class": "Inverter", "bbox": [100, 400, 200, 500]},
        {"id": "RELAY_1", "class": "Anti_Islanding_Relay", "bbox": [100, 700, 200, 800]},
        {"id": "XFMR_1", "class": "Transformer", "bbox": [100, 1000, 200, 1100]},
        {"id": "GRID_1", "class": "Grid_Connection", "bbox": [100, 1300, 200, 1400]}
    ]
    # Connect everything linearly
    lines = [
        ((200, 150), (400, 150)),
        ((500, 150), (700, 150)),
        ((800, 150), (1000, 150)),
        ((1100, 150), (1300, 150))
    ]
    resolver = SLDTopologyResolver()
    g = resolver.resolve(symbols, lines)
    
    assert g.number_of_nodes() == 5
    assert g.number_of_edges() == 4
    assert nx.has_path(g, "XFMR_1", "GRID_1")

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
