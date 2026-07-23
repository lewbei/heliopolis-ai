import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest

from app_logic import (
    get_state_from_region,
    parse_mean_slope,
    deterministic_hash,
    generate_co_owners,
    _imperial_string_to_parts,
    _sld_node_style,
    build_land_metadata,
    compute_assessment,
    project_lifecycle_cashflows,
    generate_precise_terrain,
    _synthetic_elevation_grid,
)


def test_get_state_from_region():
    assert get_state_from_region("Kedah (Kubang Pasu)") == "Kedah"
    assert get_state_from_region("Perak (Larut dan Matang)") == "Perak"
    assert get_state_from_region("Johor Bahru") == "Johor"
    assert get_state_from_region("Unknown Place") == "Selangor"


def test_parse_mean_slope():
    assert parse_mean_slope("Severe Ridge (12.50° mean)") == pytest.approx(12.5)
    assert parse_mean_slope("Optimal Plain") == pytest.approx(2.1)
    assert parse_mean_slope("Rolling Hills") == pytest.approx(8.5)
    assert parse_mean_slope("No match") == pytest.approx(37.7)


def test_detinistic_hash_is_deterministic():
    assert deterministic_hash("abc") == deterministic_hash("abc")
    assert deterministic_hash("abc") != deterministic_hash("abd")


def test_generate_co_owners():
    owners = generate_co_owners(3, "MY-SITE-0101")
    assert len(owners) == 3
    total_shares = sum(int(o["share"].split("/")[0]) for o in owners)
    assert total_shares == 120
    assert owners[0]["name"] == "Solarvest Development Sdn Bhd"


def test_imperial_string_to_parts():
    acres, roods, poles = _imperial_string_to_parts("12 Ekar 2 Rood 15 Pole")
    assert acres == 12.0
    assert roods == 2.0
    assert poles == 15.0

    acres, roods, poles = _imperial_string_to_parts("5 ekar")
    assert acres == 5.0
    assert roods == 0.0
    assert poles == 0.0


def test_sld_node_style():
    style = _sld_node_style("Inverter", "INV_1")
    assert style["color"] == "#60a5fa"
    assert "INV_1" in style["label"]

    unknown = _sld_node_style("Unknown", "X_1")
    assert unknown["color"] == "#9ca3af"


def test_build_land_metadata():
    owners = generate_co_owners(3, "MY-SITE-0001")
    land_meta, hectares, sq_m, acres, roods, poles, html = build_land_metadata(
        title_no="GRN 12345",
        lot_no="Lot 999",
        state="Kedah",
        zoning="Pertanian",
        acres=12.0,
        roods=2.0,
        poles=15.0,
        caveats=False,
        charges=False,
        reserve=False,
        owners_list=owners,
    )
    assert land_meta.title_no == "GRN 12345"
    assert land_meta.state == "Kedah"
    # Pertanian zoning should be Flagged/Risky pending NLC Section 124 conversion.
    assert land_meta.legal_assessment.status == "Flagged/Risky"
    assert hectares > 1.0
    assert sq_m > 10000.0
    assert "Solarvest" in html


def test_synthetic_elevation_grid():
    optimal = _synthetic_elevation_grid("Optimal")
    severe = _synthetic_elevation_grid("Severe")
    assert optimal.shape == severe.shape
    assert np.max(severe) > np.max(optimal)


def test_generate_precise_terrain_matches_target_slope():
    target = 8.5
    grid = generate_precise_terrain(target)
    gy, gx = np.gradient(grid, 10.0)
    slope_deg = np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))
    assert np.mean(slope_deg) == pytest.approx(target, abs=0.3)


def test_project_lifecycle_cashflows_shape():
    projection = project_lifecycle_cashflows(
        capacity_mwp=1.0,
        annual_yield_mwh=1500.0,
        adjusted_capex_rm=3_000_000.0,
        bess_capex_rm=0.0,
    )
    assert len(projection["cash_flows"]) == 22
    assert projection["cash_flows"][0] < 0
    assert projection["discounted_costs"] > 0.0
    assert projection["discounted_energy"] > 0.0


def test_compute_assessment():
    owners = generate_co_owners(1, "MY-SITE-0002")
    land_meta, *_ = build_land_metadata(
        title_no="GRN 54321",
        lot_no="Lot 111",
        state="Kedah",
        zoning="Pertanian",
        acres=5.0,
        roods=0.0,
        poles=0.0,
        caveats=False,
        charges=False,
        reserve=False,
        owners_list=owners,
    )
    result = compute_assessment(
        land_meta=land_meta,
        slope_profile="Optimal Plain",
        ac_capacity=1.0,
        substation_mva=10.0,
    )
    assert "terrain_model" in result
    assert "grid_audit" in result
    assert "feasibility" in result
    assert "sld_graph" in result
    assert "manifest" in result
    assert not result["grid_audit"].bess_specification.is_bess_required
