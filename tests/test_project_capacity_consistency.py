"""High-stakes MAIC Issue #17: changed AC capacity must change financials and
source title area must never be swapped with an unrelated Perak demo preset.
These are synthetic model tests; NOT solar engineering feasibility evidence.
"""

import math
from unittest.mock import patch

import numpy as np
import pytest

from app_logic import build_land_metadata, compute_assessment
from solar_agent import (
    LandTitleParser,
    screen_land_footprint,
    DEFAULT_AC_TO_DC_RATIO,
    DEFAULT_LAND_SQM_PER_MWP,
    DEFAULT_USABLE_LAND_FRACTION,
)


def _case(area_acres, caveat=True):
    meta, *_ = build_land_metadata(
        title_no="SYNTH-GRN-2026-001",
        lot_no="SYNTH-LOT-001",
        state="Perak",
        zoning="Bangunan",
        acres=float(area_acres),
        roods=0.0,
        poles=0.0,
        caveats=caveat,
        charges=False,
        reserve=False,
        owners_list=[
            {"name": "SYNTHETIC PERSON ALPHA", "id": "SYNTH-ID-0001", "share": "60/120"},
            {"name": "SYNTHETIC PERSON BETA", "id": "SYNTH-ID-0002", "share": "60/120"},
        ],
        source_type="SYNTHETIC_PITCH_INPUT",
    )
    return meta


def run_case(land, ac):
    return compute_assessment(
        land_meta=land, slope_profile="Optimal Flat Plain (2.1° mean)",
        ac_capacity=ac, substation_mva=15.0, voltage_class="MV",
        site_mode="Standard Presets",
        scenario="lss_ppa", hypothetical_bess=False,
    )


@pytest.mark.parametrize("capacity", [2.0, 3.21])
def test_actual_two_acre_source_title_rejects_oversized_proposals(capacity):
    land = _case(2.0)
    result = run_case(land, capacity)
    area = result["land_footprint_screen"]
    financial = result["feasibility"]
    assert area.status == "NEEDS_REVIEW"
    assert area.land_area_sqm == pytest.approx(2.0 * 4046.8564, abs=0.1)
    assert area.max_screened_ac_mw == pytest.approx(0.51, abs=0.01)
    assert area.proposed_ac_mw == capacity
    assert financial.capacity_mwp == pytest.approx(capacity / 0.85, abs=0.001)
    assert financial.financial_status == "NEEDS_REVIEW_INCOMPATIBLE_LAND_FOOTPRINT"
    assert financial.npv_rm is None
    assert financial.irr_percent is None
    assert financial.payback_years is None
    assert financial.annual_yield_mwh > 0  # hypothetical gross output, NOT parcel feasibility
    assert result["manifest"].seda_application.Part_C_Proposed_AC_Capacity_kWac == pytest.approx(capacity * 1000)
    assert result["manifest"].seda_application.Part_C_Proposed_DC_Capacity_kWp == pytest.approx(financial.capacity_mwp * 1000, abs=1.0)
    assert land.has_caveats
    assert land.legal_assessment.status == "Flagged/Risky"
    assert len(land.owners) == 2
    assert sum(o.calculated_share_float for o in land.owners) == 1.0
    assert result["data_provenance"]["land"] == "SYNTHETIC_PITCH_INPUT"


def test_capacity_changes_yield_capex_and_npv_on_same_adequate_parcel():
    land = _case(25.0, caveat=False)
    big = run_case(land, 3.21)
    small = run_case(land, 2.0)
    max_rating = big["land_footprint_screen"].max_screened_ac_mw
    assert max_rating > 3.21
    for result in (big, small):
        assert result["land_footprint_screen"].status == "WITHIN_ILLUSTRATIVE_AREA_NOT_APPROVAL"
        assert result["feasibility"].financial_status == "ILLUSTRATIVE_LSS_PPA_NO_SIGNED_CONTRACT"
        assert result["feasibility"].npv_rm is not None
        assert result["feasibility"].irr_percent is not None
    fb, fs = big["feasibility"], small["feasibility"]
    assert fb.capacity_mwp == pytest.approx(3.21 / 0.85, abs=0.001)
    assert fs.capacity_mwp == pytest.approx(2.0 / 0.85, abs=0.001)
    assert fb.annual_yield_mwh > fs.annual_yield_mwh
    assert fb.grading_adjusted_capex_rm > fs.grading_adjusted_capex_rm
    assert fb.npv_rm != fs.npv_rm
    assert fb.base_capex_rm > fs.base_capex_rm
    assert big["grid_audit"].substation_injection_percent != small["grid_audit"].substation_injection_percent
    assert big["manifest"].seda_application.Part_C_Proposed_AC_Capacity_kWac == 3210.0
    assert small["manifest"].seda_application.Part_C_Proposed_AC_Capacity_kWac == 2000.0
    assert land.area_sq_meters == pytest.approx(25.0 * 4046.8564, abs=0.1)


def test_lot_area_changes_the_footprint_limit_not_proposed_plant_size():
    two_acres = run_case(_case(2.0), 2.0)
    ample_land = run_case(_case(25.0), 2.0)
    assert two_acres["land_footprint_screen"].status == "NEEDS_REVIEW"
    assert ample_land["land_footprint_screen"].status == "WITHIN_ILLUSTRATIVE_AREA_NOT_APPROVAL"
    assert two_acres["feasibility"].capacity_mwp == ample_land["feasibility"].capacity_mwp
    assert ample_land["land_footprint_screen"].max_screened_ac_mw > two_acres["land_footprint_screen"].max_screened_ac_mw


def test_footprint_formula_matches_explicit_documented_assumptions():
    screen = screen_land_footprint(2.0 * 4046.8564, proposed_ac_mw=3.21)
    manual_limit = (
        2.0 * 4046.8564 * DEFAULT_USABLE_LAND_FRACTION
        / DEFAULT_LAND_SQM_PER_MWP * DEFAULT_AC_TO_DC_RATIO
    )
    assert screen.max_screened_ac_mw == pytest.approx(manual_limit, abs=0.000001)
    assert screen.estimated_land_required_sqm > screen.land_area_sqm
    assert screen.land_shortfall_sqm > 0.0
    assert "not surveyed buildable land" in " ".join(screen.findings).lower()


@pytest.mark.parametrize("area,capacity,ratio", [
    (float("nan"), 2.0, 0.85),
    (1000.0, float("inf"), 0.85),
    (1000.0, 2.0, 0.0),
    (1000.0, 2.0, -0.9),
    (1000.0, 2.0, 1.2),
    (-2.0, 2.0, 0.85),
    (1000.0, 0.0, 0.85),
])
def test_fail_closed_on_invalid_footprint_inputs(area, capacity, ratio):
    with pytest.raises(ValueError):
        screen_land_footprint(area, capacity, ratio)


def test_synthetic_title_image_fields_are_not_replaced_by_sidebar_values():
    extracted = {
        "title_no": "SYNTH-GRN-2026-001",
        "lot_no": "SYNTH-LOT-001",
        "state": "Perak",
        "district": "Synthetic District",
        "mukim": "Synthetic Mukim",
        "zoning": "Bangunan",
        "area_acres": 2.0,
        "area_roods": 0.0,
        "area_poles": 0.0,
        "has_caveats": True,
        "has_charges": False,
        "is_malay_reserve": False,
        "owners": [
            {"name": "SYNTHETIC PERSON ALPHA", "ic_or_co_no": "SYNTH-ID-0001", "share_fraction": "60/120"},
            {"name": "SYNTHETIC PERSON BETA", "ic_or_co_no": "SYNTH-ID-0002", "share_fraction": "60/120"},
        ],
    }
    with patch("solar_agent.heliopolis_ocr.parse_land_title_image", return_value=extracted):
        land, *_ = build_land_metadata(
            title_no="NOT-THE-UPLOAD",
            lot_no="NOT-THE-UPLOAD",
            state="Kedah",
            zoning="Pertanian",
            acres=12.0, roods=2.0, poles=15.0,
            caveats=False, charges=False, reserve=False,
            owners_list=[{"name": "Fictional sidebar", "id": "DEMO", "share": "1/1"}],
            title_image_path="synthetic-pitch-input.png",
        )
    assert land.title_no == "SYNTH-GRN-2026-001"
    assert land.lot_no == "SYNTH-LOT-001"
    assert land.area_sq_meters == pytest.approx(2.0 * 4046.8564, abs=0.1)
    assert len(land.owners) == 2
    assert land.has_caveats is True
    assessment = run_case(land, 3.21)
    assert assessment["land_footprint_screen"].status == "NEEDS_REVIEW"
    assert assessment["data_provenance"]["land"] == "OCR_EXTRACTED_UNVERIFIED"
