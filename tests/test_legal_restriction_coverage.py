"""Focused negative controls for preliminary Malaysian title screening.

Synthetic fixtures cannot establish a legal judgement or state-level land-office
decision. These tests cover fail-closed behavior on the model's supported flags.
"""

import pytest

from solar_agent import (
    DocumentReviewRequired,
    LandTitleParser,
)
from app_logic import build_land_metadata


@pytest.mark.parametrize("flag,fragment", [
    ("has_caveats", "caveat"),
    ("has_charges", "charge"),
    ("is_malay_reserve", "malay reserve"),
])
def test_recorded_encumbrance_never_returns_clean_title(flag, fragment):
    options = {
        "zoning": "Bangunan",
        "has_caveats": False,
        "has_charges": False,
        "is_malay_reserve": False,
        "poa": LandTitleParser._compute_poa([]),
    }
    options[flag] = True
    screen = LandTitleParser._compute_legal_assessment(**options)
    assert screen.status == "Flagged/Risky"
    assert any(fragment in finding.lower() for finding in screen.findings)
    assert all("approved" not in finding.lower() for finding in screen.findings)


@pytest.mark.parametrize("zoning", ["Pertanian", "", "Unknown Category", "PERINDUSTRIAN"])
def test_land_use_is_only_preliminary_screening(zoning):
    poa = LandTitleParser._compute_poa([])
    screen = LandTitleParser._compute_legal_assessment(
        zoning=zoning, has_caveats=False, has_charges=False,
        is_malay_reserve=False, poa=poa,
    )
    assert screen.status in ("Needs Legal Review", "Flagged/Risky")
    assert screen.status != "Approved"
    if zoning != "PERINDUSTRIAN":
        assert screen.status == "Flagged/Risky"


def test_single_proprietor_also_requires_title_review():
    poa = LandTitleParser._compute_poa([])
    screen = LandTitleParser._compute_legal_assessment(
        "Bangunan", False, False, False, poa,
    )
    assert screen.status == "Needs Legal Review"
    assert poa.is_poa_required is None
    assert poa.min_co_owners_needed is None


def test_manual_owner_shares_not_100_percent_fail_closed():
    with pytest.raises(DocumentReviewRequired, match="100%"):
        build_land_metadata(
            title_no="SYNTHETIC-1", lot_no="SYNTHETIC-2",
            state="Kedah", zoning="Bangunan", acres=1.0,
            roods=0, poles=0, caveats=False, charges=False,
            reserve=False,
            owners_list=[
                {"name": "Fixture A", "id": "DEMO-A", "share": "2/3"},
                {"name": "Fixture B", "id": "DEMO-B", "share": "1/6"},
            ],
        )
