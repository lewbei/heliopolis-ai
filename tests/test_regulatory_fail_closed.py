"""Adversarial, synthetic tests. These are not field legal/grid certification."""

import numpy as np
import pytest
from unittest.mock import patch

from app_logic import build_land_metadata, validate_inputs
from solar_agent import (
    CivilSlopeAnalyzer,
    DocumentReviewRequired,
    FormFiller,
    LandTitleParser,
    SCENARIO_C_I_NEM,
    TNBSubstationCapacityValidator,
    YieldFeasibilityEngine,
    screen_solar_atap_non_domestic,
)


def _title_record():
    return {
        "title_no": "SYNTHETIC GRN 100",
        "lot_no": "SYNTHETIC Lot 20",
        "state": "Kedah",
        "district": "Kubang Pasu",
        "zoning": "Bangunan",
        "area_acres": 1.0,
        "area_roods": 0.0,
        "area_poles": 0.0,
        "has_caveats": False,
        "has_charges": False,
        "is_malay_reserve": False,
        "owners": [
            {"name": "Fixture A", "ic_or_co_no": "DEMO-A", "share_fraction": "1/2"},
            {"name": "Fixture B", "ic_or_co_no": "DEMO-B", "share_fraction": "1/2"},
        ],
    }


@pytest.mark.parametrize("bad", ["1/0", "NaN", "-0.1", "2/1", "", "Inf", "abc"])
def test_owner_shares_reject_unsafe_values(bad):
    with pytest.raises(ValueError):
        LandTitleParser.parse_fraction_strict(bad)


def test_coowners_cannot_lease_from_majority_share_arithmetic():
    title = _title_record()
    title["owners"] = [
        {"name": "Fixture A", "ic_or_co_no": "DEMO-A", "share_fraction": "7/10"},
        {"name": "Fixture B", "ic_or_co_no": "DEMO-B", "share_fraction": "3/10"},
    ]
    with patch("solar_agent.heliopolis_ocr.parse_land_title_image", return_value=title):
        result = LandTitleParser.from_image("fake-path.png")
    assert result.legal_assessment.status == "Needs Legal Review"
    assert any("do not establish authority" in finding
               for finding in result.legal_assessment.findings)
    assert result.legal_assessment.poa_compliance.is_poa_required
    assert result.review_status == "NEEDS_LEGAL_REVIEW"


@pytest.mark.parametrize("extra", [
    {"area_hectares_stated": 123.45},
    {"area_sq_meters_stated": 250_000.0},
    {"area_sq_meters_stated": -1.0},
    {"area_hectares_stated": "not a number"},
])
def test_ocr_conflicting_area_statements_fail_closed(extra):
    title = _title_record()
    title.update(extra)
    with patch("solar_agent.heliopolis_ocr.parse_land_title_image", return_value=title):
        with pytest.raises(DocumentReviewRequired, match="area|Area|hectares|meter"):
            LandTitleParser.from_image("fake-path.png")


def test_title_ocr_matching_metric_fields_remain_unverified():
    title = _title_record()
    hectares, sqm = LandTitleParser.convert_imperial_to_metric(1.0, 0.0, 0.0)
    title["area_hectares_stated"] = hectares
    title["area_sq_meters_stated"] = sqm
    with patch("solar_agent.heliopolis_ocr.parse_land_title_image", return_value=title):
        result = LandTitleParser.from_image("fake-path.png")
    assert result.source_type == "OCR_EXTRACTED_UNVERIFIED"
    assert result.legal_assessment.status != "Approved"


def test_form_input_no_longer_inherits_demo_mukim_or_company():
    meta, *_ = build_land_metadata(
        title_no="SYNTHETIC GRN X", lot_no="Lot Z", state="Johor",
        zoning="Bangunan", acres=3.0, roods=0, poles=0,
        caveats=False, charges=False, reserve=False,
        owners_list=[{"name": "Fixture", "id": "DEMO-X", "share": "1/1"}],
        project_company_name="", project_company_reg_no="",
    )
    assert meta.district == ""
    assert meta.mukim == ""
    assert meta.project_company_name == ""
    assert meta.source_type == "USER_ENTERED_UNVERIFIED"
    assert meta.legal_assessment.status == "Needs Legal Review"


def test_form_invalid_owner_total_and_rood_pole_range():
    base = dict(
        acres=1, roods=0, poles=0, ac_capacity=0.5, substation_mva=10.0,
        state="Johor", title_no="DEMO-X", lot_no="DEMO-1",
    )
    too_few = validate_inputs(
        **base, owners_list=[{"name": "A", "id": "DEMO", "share": "1/2"}]
    )
    assert any("100%" in msg for msg in too_few)
    invalid = validate_inputs(
        **{**base, "roods": 4.0, "poles": 40},
        owners_list=[{"name": "A", "id": "DEMO", "share": "1/1"}],
    )
    assert any("roods" in msg for msg in invalid)
    bad_fraction = validate_inputs(
        **base, owners_list=[{"name": "A", "id": "DEMO", "share": "1/0"}]
    )
    assert any("fraction" in msg for msg in bad_fraction)


def _tech(scenario="lss_ppa"):
    land = LandTitleParser().parse("")
    terrain = CivilSlopeAnalyzer.analyze_topography(np.zeros((5, 5)), 10.0)
    grid = TNBSubstationCapacityValidator.audit_injection(0.9, 15.0)
    return land, YieldFeasibilityEngine(land, terrain, grid).calculate(scenario=scenario)


def test_no_fabricated_voltage_transformer_or_applicant_for_lss():
    land, tech = _tech()
    land.project_company_name = ""
    land.project_company_reg_no = ""
    manifest = FormFiller.generate_manifest(land, tech, proposed_ac_mw=0.9)
    assert manifest.tnb_grid_request.Interconnection_Voltage_Level_kV is None
    assert manifest.tnb_grid_request.Transformer_Capacity_MVA is None
    assert manifest.seda_application.Part_A_Applicant_Name == "APPLICANT_NOT_PROVIDED"
    assert manifest.nemas_checklist.estimated_regulatory_fee_rm is None


def test_historical_nova_without_voltage_never_quotes_CAS():
    land, tech = _tech(SCENARIO_C_I_NEM)
    manifest = FormFiller.generate_manifest(land, tech, proposed_ac_mw=0.9)
    study = manifest.nemas_checklist
    assert not study.study_applicability_known
    assert study.voltage_class == "UNKNOWN"
    assert study.estimated_regulatory_fee_rm is None
    assert "VOLTAGE_UNVERIFIED" in study.assessment_type
    assert "2025" in study.source_version


@pytest.mark.parametrize("voltage,study_required,fee", [
    ("LV", True, 8000.0),
    ("MV", True, 8000.0),
    ("HV", True, None),
])
def test_nova_study_depends_on_explicit_voltage(voltage, study_required, fee):
    land, tech = _tech(SCENARIO_C_I_NEM)
    study = FormFiller.generate_manifest(
        land, tech, proposed_ac_mw=0.9, voltage_class=voltage,
    ).nemas_checklist
    assert study.study_applicability_known
    assert study.is_nemas_required is study_required
    assert study.estimated_regulatory_fee_rm == fee
    assert "NOVA" in study.assessment_type
    assert study.source_url.startswith("https://www.seda.gov.my/")


@pytest.mark.parametrize("kw,md,expected", [
    (1000.01, 2000.0, "OUTSIDE_ATAP_NON_DOMESTIC_CAP"),
    (900.0, None, "MAXIMUM_DEMAND_NOT_PROVIDED"),
    (900.0, 850.0, "EXCEEDS_VERIFIED_MAXIMUM_DEMAND"),
    (900.0, 900.0, "CAPACITY_SCREEN_ONLY_FURTHER_REVIEW_REQUIRED"),
])
def test_atap_capacity_only_screen(kw, md, expected):
    result = screen_solar_atap_non_domestic(kw, md)
    assert result.status == expected
    assert result.export_offset_max_years == 10
    assert any("year 11" in note for note in result.notes)


@pytest.mark.parametrize("kw,md", [
    (float("nan"), 100.0), (-1.0, 100.0),
    (50.0, 0.0), (50.0, float("inf")),
])
def test_atap_screen_invalid_numeric_inputs(kw, md):
    with pytest.raises(ValueError):
        screen_solar_atap_non_domestic(kw, md)


def test_atap_oversize_demo_report_cannot_imply_eligibility():
    land, tech = _tech("lss_ppa")
    m = FormFiller.generate_manifest(
        land, tech, proposed_ac_mw=5.87, maximum_demand_kw=6000.0
    )
    assert m.solar_atap_precheck.status == "OUTSIDE_ATAP_NON_DOMESTIC_CAP"
    assert m.nemas_checklist.estimated_regulatory_fee_rm is None
