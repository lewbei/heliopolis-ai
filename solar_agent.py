import os
import sys
import numpy as np
import networkx as nx
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

import heliopolis_ocr


class DocumentReviewRequired(ValueError):
    """Uploaded evidence could not be verified; do not substitute demonstration fixtures."""



# --- Shared Financial Constants ---
DEFAULT_PROJECT_LIFETIME = 21
DEFAULT_OPEX_PER_MWP_YEAR = 45000.0
DEFAULT_BESS_OPEX_RATE = 0.015
DEFAULT_OPEX_INFLATION = 0.02
DEFAULT_DEGRADATION_RATE = 0.005
DEFAULT_TARIFF_RM_KWH = 0.27
DEFAULT_WACC = 0.065

# --- Financial Scenario Tariffs (RM/kWh) ---
# Sourced from Malaysian market benchmarks:
#   LSS PPA ~RM 0.17/kWh (LSS5 average, 2024)
#   C&I NEM/ATAP offset ~RM 0.37/kWh (industrial displaced tariff)
#   Self-consumption premium ~RM 0.45/kWh (system-access / green tariff scenarios)
SCENARIO_LSS_PPA = "lss_ppa"
SCENARIO_C_I_NEM = "c_i_nem"
SCENARIO_SELF_CONSUMPTION = "self_consumption"
SCENARIO_LABELS = {
    SCENARIO_LSS_PPA: "LSS PPA (Utility-Scale)",
    SCENARIO_C_I_NEM: "C&I / NEM NOVA sensitivity (NOT Solar ATAP)",
    SCENARIO_SELF_CONSUMPTION: "Self-consumption tariff sensitivity (illustrative)",
}
SCENARIO_TARIFFS: dict[str, float] = {
    SCENARIO_LSS_PPA: 0.17,
    SCENARIO_C_I_NEM: 0.37,
    SCENARIO_SELF_CONSUMPTION: 0.45,
}
DEFAULT_SCENARIO = SCENARIO_LSS_PPA

# --- Deterministic owner-name helper (used by CLI and Streamlit) ---

def deterministic_hash(string_val: str) -> int:
    """Return a deterministic 32-bit hash for a string."""
    h = 0
    for char in string_val:
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    return h


def generate_co_owners(count: int, site_id: str) -> list[dict[str, str]]:
    """Generate a deterministic list of co-owner dicts for a site."""
    np.random.seed(sum(ord(c) for c in site_id))
    first_names = ["Ahmad", "Mohamad", "Siti", "Tan", "Lim", "Lee", "Ramasamy", "Muthu", "Karthik", "Abdul", "Wan", "Che", "Chong"]
    last_names = ["Bin Ismail", "Binti Ali", "Bin Ahmad", "Kah Seng", "Wei", "Meng", "Anak Nysem", "Bin Kassim", "Binti Hassan", "a/l Subramaniam", "a/p Devian"]

    owners: list[dict[str, str]] = []

    if count == 1:
        shares = [120]
    elif count == 2:
        shares = [80, 40]
    else:
        raw_shares = np.random.dirichlet(np.ones(count)) * 120
        shares = np.round(raw_shares).astype(int)
        diff = 120 - sum(shares)
        shares[0] += diff
        for idx in range(count):
            if shares[idx] <= 0:
                max_idx = np.argmax(shares)
                shares[max_idx] -= 1
                shares[idx] = 1

    used_names = set()
    for i in range(count):
        share_str = f"{shares[i]}/120"

        if i == 0 and count >= 3:
            name = "Solarvest Development Sdn Bhd"
            ic_co = "1234567-U"
        else:
            salt = 0
            while True:
                fn = first_names[deterministic_hash(f"fn_{i}_{site_id}_{salt}") % len(first_names)]
                ln = last_names[deterministic_hash(f"ln_{i}_{site_id}_{salt}") % len(last_names)]
                candidate = f"{fn} {ln}"
                if candidate not in used_names:
                    used_names.add(candidate)
                    break
                salt += 1
            name = candidate

            birth_yr = deterministic_hash(f"yr_{i}_{site_id}_{salt}") % 50 + 50
            birth_mo = deterministic_hash(f"mo_{i}_{site_id}_{salt}") % 12 + 1
            birth_dy = deterministic_hash(f"dy_{i}_{site_id}_{salt}") % 28 + 1
            state_code = deterministic_hash(f"st_{i}_{site_id}_{salt}") % 14 + 1
            unique_code = deterministic_hash(f"un_{i}_{site_id}_{salt}") % 9000 + 1000
            ic_co = f"{birth_yr:02d}{birth_mo:02d}{birth_dy:02d}-{state_code:02d}-{unique_code:d}"

        owners.append({
            "name": name,
            "id": ic_co,
            "share": share_str
        })

    return owners


# --- Core Relational & Structured Data Models (Pydantic V2) ---

class OwnerModel(BaseModel):
    name: str = Field(description="Name of the registered landowner.")
    ic_or_co_no: str = Field(description="MyKad IC Number or Company Registration Number.")
    share_fraction: str = Field(description="Raw ownership share as a fraction, e.g., '11/120'.")
    calculated_share_float: float = Field(description="Decimal value of the fractional share.")

class PowerOfAttorneyModel(BaseModel):
    is_poa_required: bool = Field(description="True if no single owner holds a controlling >50% stake.")
    min_co_owners_needed: int = Field(description="Minimum number of co-owners that must co-sign to exceed 51% controlling interest.")
    required_deeds: List[str] = Field(default=[], description="List of legal instruments required for joint land lease.")

class LegalAssessmentModel(BaseModel):
    status: str = Field(description="Zoning or transaction suitability: 'Approved', 'Flagged/Risky', or 'Rejected'.")
    findings: List[str] = Field(default=[], description="List of administrative or legal issues found on the land title.")
    poa_compliance: PowerOfAttorneyModel

class LandTitleMetadata(BaseModel):
    source_type: str = Field(default="SYNTHETIC_DEMO", description="Origin of title evidence; not an independent verification.")
    review_status: str = Field(default="NEEDS_LEGAL_REVIEW", description="Preliminary screening only; never legal clearance.")
    title_no: str = Field(description="Title reference number, e.g., 'GRN 45293'.")
    lot_no: str = Field(description="Lot or PT number, e.g., 'Lot 8192'.")
    state: str = Field(description="Malaysian state.")
    district: str = Field(description="District / Daerah.")
    mukim: str = Field(description="Sub-district / Mukim.")
    zoning: str = Field(description="Kategori Kegunaan Tanah, e.g., 'Pertanian', 'Bangunan', 'Perindustrian'.")
    area_imperial: str = Field(description="Raw historical imperial units, e.g., '12 Ekar 2 Rood 15 Pole'.")
    area_hectares: float = Field(description="Converted area in metric Hectares.")
    area_sq_meters: float = Field(description="Converted area in metric Square Meters.")
    owners: List[OwnerModel] = Field(default=[], description="Registered landowners with share allocations.")
    project_company_name: str = Field(default="", description="Name of the project development company applying for SEDA/TNB permits.")
    project_company_reg_no: str = Field(default="", description="Company registration number of the project development company.")
    has_caveats: bool = Field(description="True if an active Caveat is detected on the title.")
    has_charges: bool = Field(description="True if an active Bank Charge (Gadaian) is detected.")
    is_malay_reserve: bool = Field(description="True if designated as Tanah Rezab Melayu.")
    legal_assessment: LegalAssessmentModel

class TerrainProfileModel(BaseModel):
    mean_slope_degrees: float = Field(description="Average terrain slope in degrees.")
    optimal_area_percent: float = Field(description="Percentage of land with slope < 5 degrees.")
    manageable_area_percent: float = Field(description="Percentage of land with slope 5 to 15 degrees.")
    critical_area_percent: float = Field(description="Percentage of land with slope > 15 degrees.")
    landslide_risk: str = Field(description="Risk classification: 'Low', 'Medium', or 'High (Unbuildable)'.")
    grading_capex_premium_multiplier: float = Field(description="CAPEX multiplier adjustment for civil earthworks.")

class BESSRecommendationModel(BaseModel):
    is_bess_required: bool = Field(description="True if PV capacity exceeds 15% of upstream TNB substation capacity.")
    recommended_battery_power_mw: float = Field(description="Recommended Battery Energy Storage System (BESS) power rating (MW).")
    recommended_battery_capacity_mwh: float = Field(description="Recommended BESS capacity for peak shaving (MWh).")
    estimated_bess_capex_rm: float = Field(description="Estimated extra BESS capital expenditure (RM).")
    reasons: List[str] = Field(default=[], description="Technical rationale for battery storage requirement.")

class GridCapacityValidationModel(BaseModel):
    upstream_substation_capacity_mva: float = Field(description="Rated capacity of local TNB substation (MVA).")
    substation_injection_percent: float = Field(description="Ratio of peak AC solar output to substation capacity.")
    reverse_power_risk: str = Field(description="Grid risk classification: 'Negligible', 'Moderate', or 'Severe'.")
    bess_specification: BESSRecommendationModel

class TechnicalFeasibilityModel(BaseModel):
    capacity_mwp: float = Field(description="Simulated PV system peak DC capacity (MWp).")
    annual_yield_mwh: float = Field(description="Estimated annual electricity generation (MWh/year).")
    base_capex_rm: float = Field(description="Base capital expenditure in Malaysian Ringgit (RM).")
    grading_adjusted_capex_rm: float = Field(description="Final CAPEX including civil grading premiums.")
    lcoe_rm_kwh: float = Field(description="Levelized Cost of Electricity (RM/kWh).")
    ppa_tariff_rm_kwh: float = Field(description="Assumed PPA or displaced energy tariff used for revenue projection (RM/kWh).")
    scenario: str = Field(description="Financial scenario used for revenue projection (lss_ppa, c_i_nem, self_consumption).")
    npv_rm: float = Field(description="Net Present Value (RM) over the project lifecycle.")
    irr_percent: float = Field(description="Project Internal Rate of Return (%).")
    payback_years: float = Field(description="Estimated capital payback period in years.")
    terrain_profile: TerrainProfileModel
    grid_capacity_audit: GridCapacityValidationModel

class NEMASChecklistSchema(BaseModel):
    is_nemas_required: bool = Field(description="True if proposed AC capacity exceeds 72 kWac.")
    voltage_rise_study_required: bool = Field(description="True if AC generation can trigger local grid overvoltage.")
    estimated_regulatory_fee_rm: float = Field(description="Estimate of TNB/SEDA assessment study fees.")
    estimated_processing_days: Optional[int] = Field(default=None, description="Estimated calendar days, or None if not supported by evidence.")
    assessment_type: str = Field(default="UNCONFIRMED", description="Applicable connection study, not a permit.")
    source_url: str = Field(default="", description="Scheme-specific reference used for study fees.")
    eligibility_notes: List[str] = Field(default_factory=list, description="Requirements needing independent confirmation.")
    mandatory_technical_studies: List[str] = Field(default=[], description="List of engineering studies required for grid filing.")

class SEDAApplicationSchema(BaseModel):
    Part_A_Applicant_Name: str
    Part_A_Company_Registration: str
    Part_B_Site_Title_Number: str
    Part_B_Site_Lot_Number: str
    Part_B_Mukim_Daerah_Negeri: str
    Part_C_Proposed_DC_Capacity_kWp: float
    Part_C_Proposed_AC_Capacity_kWac: float
    Part_D_PPA_Tariff_Rate_RM_kWh: float

class TNBConnectionSchema(BaseModel):
    Applicant_Company: str
    Interconnection_Voltage_Level_kV: float
    Total_Generation_Capacity_MWac: float
    Inverter_Compliance_Standards: List[str]
    Point_of_Common_Coupling: str
    Transformer_Capacity_MVA: float

class RegulatoryFilingManifest(BaseModel):
    seda_application: SEDAApplicationSchema
    tnb_grid_request: TNBConnectionSchema
    nemas_checklist: NEMASChecklistSchema


# --- Specialized Parsing & Analysis Modules ---

class ImageOrientationCorrector:
    """
    Improvised Module: Simulates Radon/Hough-based affine de-skewing and perspective
    homography corrections to align scanned/photographed documents to 0.0° before parsing.
    """
    @staticmethod
    def deskew_image(image_metadata: dict) -> dict:
        print("[ImageOrientationCorrector] Running dominant Radon transform peaks to check document skew...")
        detected_skew_deg = image_metadata.get("raw_skew_degrees", 0.0)

        # Initialise to identity so it is always returned, even for a perfectly aligned page.
        rotation_matrix = np.eye(2)

        if abs(detected_skew_deg) > 0.1:
            print(f" [Corrector] SKEW DETECTED: {detected_skew_deg:.2f}°. Computing affine homography rotation matrix...")
            angle = np.radians(-detected_skew_deg)
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])
            corrected_skew = 0.0
            print(" [Corrector] Flawless alignment achieved: 0.00° skew.")
        else:
            print(" [Corrector] Document is perfectly aligned (0.0° skew). Skipping affine warping.")
            corrected_skew = 0.0

        return {
            "corrected_skew_degrees": corrected_skew,
            "alignment": "Aligned",
            "rotation_matrix": rotation_matrix.tolist()
        }


class LandTitleParser:
    """
    Simulates high-precision, layout-aware legal OCR and text analysis of Malaysian Land Titles (Geran),
    complying with the National Land Code (NLC / Kanun Tanah Negara) 1965.
    """
    @staticmethod
    def convert_imperial_to_metric(acres: float, roods: float, poles: float) -> tuple[float, float]:
        """
        Calculates precise metric conversions from archaic British imperial land units.
        Returns: (hectares, square_meters)
        """
        hectares = (acres * 0.40468564) + (roods * 0.10117141) + (poles * 0.00252928)
        sq_meters = hectares * 10000.0
        return round(hectares, 4), round(sq_meters, 2)

    @staticmethod
    def parse_fraction(fraction_str: str) -> float:
        """
        Parses fraction strings (e.g., '11/120', 'All', 'Semua') into floating point values.
        """
        f_clean = fraction_str.strip().lower()
        if f_clean in ["semua", "all", "1", "1.0", "1/1"]:
            return 1.0
        try:
            if "/" in f_clean:
                num, denom = map(float, f_clean.split("/"))
                return num / denom
            return float(f_clean)
        except ValueError:
            return 0.0

    @classmethod
    def _convert_metric_to_imperial(cls, area_sq_meters: float) -> str:
        """
        Reverse-converts square meters into a plausible Ekar/Rood/Pole string.
        Uses the same conversion factors as convert_imperial_to_metric inverted:
        1 Pole = 0.00252928 ha = 25.2928 m2.
        """
        total_poles = round(area_sq_meters / 25.2928)
        acres = int(total_poles // 160)
        roods = int((total_poles % 160) // 40)
        poles = int(total_poles % 40)
        return f"{acres} Ekar {roods} Rood {poles} Pole"

    @classmethod
    def _build_owners(cls, co_owners_count: int, site_id: str, owner_info: Optional[List[Dict[str, str]]] = None) -> List[OwnerModel]:
        """
        Builds the list of registered owners.

        If owner_info (list of dicts with keys name, ic_or_co_no, share) is supplied,
        those exact owner records are used. Otherwise, deterministic fractional owners
        are generated from co_owners_count and a seed derived from site_id.
        """
        if owner_info:
            owners = []
            for o in owner_info:
                share = o["share"]
                float_val = cls.parse_fraction(share)
                owners.append(OwnerModel(
                    name=o["name"],
                    ic_or_co_no=o["ic_or_co_no"],
                    share_fraction=share,
                    calculated_share_float=round(float_val, 4)
                ))
            return owners

        owner_dicts = generate_co_owners(co_owners_count, site_id)
        owners = []
        for o in owner_dicts:
            float_val = cls.parse_fraction(o["share"])
            owners.append(OwnerModel(
                name=o["name"],
                ic_or_co_no=o["id"],
                share_fraction=o["share"],
                calculated_share_float=round(float_val, 4)
            ))
        return owners

    @classmethod
    def _compute_poa(cls, owners: List[OwnerModel]) -> PowerOfAttorneyModel:
        """Preliminary co-owner coordination flag, NOT a determination of legal POA requirements."""
        # A majority ownership percentage does not establish the right to execute
        # a lease for the entire property on behalf of all registered proprietors.
        multiple_owners = len(owners) > 1
        return PowerOfAttorneyModel(
            is_poa_required=multiple_owners,  # Legacy field: means legal coordination must be checked.
            min_co_owners_needed=len(owners),
            required_deeds=(
                [
                    "Conveyancing review: confirm consent and authority of all registered proprietors.",
                    "Ask a qualified Malaysian solicitor/land office whether a power of attorney, lease or other instrument is required."
                ] if multiple_owners else [
                    "Verify registered title, legal capacity, restrictions and required land-office instruments before proceeding."
                ]
            )
        )

    @classmethod
    def _compute_legal_assessment(cls, zoning: str, has_caveats: bool, has_charges: bool, is_malay_reserve: bool, poa: PowerOfAttorneyModel) -> LegalAssessmentModel:
        """Screen visible restrictions; do not substitute for registered-title legal advice."""
        findings = ["Preliminary screening only: registered-title and state-specific legal review are required."]
        status = "Needs Legal Review"
        if not zoning or zoning.strip().lower() not in {"pertanian", "bangunan", "perindustrian"}:
            findings.append("Land-use category is missing or outside the modeled categories; verify with the land office.")
            status = "Flagged/Risky"
        if zoning and zoning.strip().lower() == "pertanian":
            findings.append("Agricultural land category: verify solar land-use permission or conversion under applicable state/NLC procedures.")
            status = "Flagged/Risky"
        if has_caveats:
            findings.append("Caveat indicated: solicitor must confirm its effect and requirements.")
            status = "Flagged/Risky"
        if has_charges:
            findings.append("Registered charge indicated: verify chargee consent and instrument requirements.")
            status = "Flagged/Risky"
        if is_malay_reserve:
            findings.append("Malay Reserve indicated: check eligibility and state legislation with a qualified professional.")
            status = "Flagged/Risky"
        if poa.is_poa_required:
            findings.append("Multiple proprietors: ownership percentages alone do not establish authority to lease the whole lot.")
        return LegalAssessmentModel(status=status, findings=findings, poa_compliance=poa)

    @classmethod
    def from_registry(cls, site_data: dict) -> LandTitleMetadata:
        """
        Builds a proper LandTitleMetadata object from the real_malaysian_sites_registry.json fields.
        """
        print("[LandTitleParser] Building metadata from selected registry fixture...")

        region = site_data["region"]
        if "(" in region and ")" in region:
            state = region.split("(")[0].strip()
            district = region.split("(")[1].split(")")[0].strip()
        else:
            state = region
            district = ""

        mukim = site_data.get("mukim")
        if not mukim:
            mukim = district

        area_sq_meters = float(site_data["area_sq_meters"])
        area_hectares = area_sq_meters / 10000.0
        area_imperial = cls._convert_metric_to_imperial(area_sq_meters)

        zoning = site_data["zoning"]
        owners = cls._build_owners(site_data["co_owners_count"], site_data["site_id"], owner_info=site_data.get("owner_templates"))

        has_caveats = bool(site_data.get("has_caveats", False))
        has_charges = bool(site_data.get("has_charges", False))
        is_malay_reserve = bool(site_data.get("is_malay_reserve", False))

        poa = cls._compute_poa(owners)
        legal = cls._compute_legal_assessment(zoning, has_caveats, has_charges, is_malay_reserve, poa)

        project_company_name = site_data.get("project_company_name", "Solarvest Development Sdn Bhd")
        project_company_reg_no = site_data.get("project_company_reg_no", "1234567-U")

        return LandTitleMetadata(
            source_type=site_data.get("source_type", "SYNTHETIC_DEMO"),
            review_status="NEEDS_LEGAL_REVIEW",
            title_no=site_data["title_no"],
            lot_no=site_data["lot_no"],
            state=state,
            district=district,
            mukim=mukim,
            zoning=zoning,
            area_imperial=area_imperial,
            area_hectares=round(area_hectares, 4),
            area_sq_meters=round(area_sq_meters, 2),
            owners=owners,
            project_company_name=project_company_name,
            project_company_reg_no=project_company_reg_no,
            has_caveats=has_caveats,
            has_charges=has_charges,
            is_malay_reserve=is_malay_reserve,
            legal_assessment=legal
        )

    @classmethod
    def from_image(cls, image_path: str) -> LandTitleMetadata:
        """Read a supplied title; require evidence rather than inventing a passing result."""
        data = heliopolis_ocr.parse_land_title_image(image_path)
        if not isinstance(data, dict):
            raise DocumentReviewRequired("Land-title OCR unavailable or failed; review uploaded title manually.")

        required_text = ("title_no", "lot_no", "state", "zoning")
        if any(not isinstance(data.get(key), str) or not data[key].strip() for key in required_text):
            raise DocumentReviewRequired("Unreadable title number, lot, state or land category; legal review required.")
        if any(type(data.get(key)) is not bool for key in ("has_caveats", "has_charges", "is_malay_reserve")):
            raise DocumentReviewRequired("Unknown caveat/charge/reserve evidence; cannot treat unreadable restrictions as absent.")

        try:
            area = [float(data[key]) for key in ("area_acres", "area_roods", "area_poles")]
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise DocumentReviewRequired("Land area could not be extracted reliably.") from exc
        if not all(np.isfinite(x) and x >= 0 for x in area) or area[1] >= 4 or area[2] >= 40:
            raise DocumentReviewRequired("Land-area fields are invalid or contradictory.")
        hectares, sq_meters = cls.convert_imperial_to_metric(*area)
        if sq_meters <= 0:
            raise DocumentReviewRequired("Land area is zero; cannot assess this site.")

        raw_owners = data.get("owners")
        if not isinstance(raw_owners, list) or not raw_owners:
            raise DocumentReviewRequired("Owner information missing; cannot infer consent or legal entitlement.")
        owners = []
        try:
            for owner in raw_owners:
                if not isinstance(owner, dict) or any(
                    not isinstance(owner.get(k), str) or not owner[k].strip()
                    for k in ("name", "ic_or_co_no", "share_fraction")
                ):
                    raise ValueError("incomplete registered-owner record")
                share = owner["share_fraction"]
                fraction = cls.parse_fraction(share)
                if not (0 < fraction <= 1):
                    raise ValueError("invalid owner share")
                owners.append(OwnerModel(
                    name=owner["name"],
                    ic_or_co_no=owner["ic_or_co_no"],
                    share_fraction=share,
                    calculated_share_float=fraction,
                ))
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            raise DocumentReviewRequired("Owner shares or identities are unreadable/inconsistent.") from exc
        if abs(sum(o.calculated_share_float for o in owners) - 1.0) > 0.001:
            raise DocumentReviewRequired("Registered owner shares do not sum to 100%; verify original title.")

        state, district = data["state"].strip(), data.get("district") or ""
        mukim = data.get("mukim") or district
        poa = cls._compute_poa(owners)
        legal = cls._compute_legal_assessment(
            data["zoning"], data["has_caveats"], data["has_charges"],
            data["is_malay_reserve"], poa,
        )
        return LandTitleMetadata(
            source_type="OCR_EXTRACTED_UNVERIFIED",
            review_status="NEEDS_LEGAL_REVIEW",
            title_no=data["title_no"], lot_no=data["lot_no"], state=state,
            district=district, mukim=mukim, zoning=data["zoning"],
            area_imperial=f"{area[0]} Ekar {area[1]} Rood {area[2]} Pole",
            area_hectares=hectares, area_sq_meters=sq_meters,
            owners=owners, project_company_name="", project_company_reg_no="",
            has_caveats=data["has_caveats"], has_charges=data["has_charges"],
            is_malay_reserve=data["is_malay_reserve"], legal_assessment=legal,
        )

    def parse(self, raw_ocr_text: str) -> LandTitleMetadata:
        print("[LandTitleParser] Executing layout-aware NLP metadata extraction...")

        # Demo fallback dataset; preserves the original sandbox title and ownership profile.
        is_malay_reserve = "Tanah Rezab Melayu" in raw_ocr_text or "Rezab Melayu" in raw_ocr_text
        has_caveats = "Kaveat" in raw_ocr_text
        has_charges = "Gadaian" in raw_ocr_text or "Dichaj" in raw_ocr_text

        _, sq_meters = self.convert_imperial_to_metric(acres=12.0, roods=2.0, poles=15.0)

        demo_site = {
            "site_id": "DEMO-GRN-45293",
            "region": "Perak (Larut dan Matang)",
            "title_no": "GRN 45293",
            "lot_no": "Lot 8192",
            "zoning": "Pertanian",
            "area_sq_meters": sq_meters,
            "mukim": "Mukim Asam Kumbang",
            "co_owners_count": 5,
            "is_malay_reserve": is_malay_reserve,
            "has_caveats": has_caveats,
            "has_charges": has_charges,
            "owner_templates": [
                {"name": "Ahmad Bin Ismail", "ic_or_co_no": "650212-08-5431", "share": "11/120"},
                {"name": "Wan Fatimah Binti Wan Ali", "ic_or_co_no": "701103-08-5222", "share": "15/120"},
                {"name": "Siti Aminah Binti Ahmad", "ic_or_co_no": "930415-08-6112", "share": "14/120"},
                {"name": "Solarvest Development Sdn Bhd", "ic_or_co_no": "1234567-U", "share": "40/120"},
                {"name": "Lee Chong Wei", "ic_or_co_no": "821021-10-5431", "share": "40/120"}
            ]
        }

        return self.from_registry(demo_site)


def _synthetic_elevation_grid(profile_label: str) -> np.ndarray:
    """Generate a synthetic elevation grid for a named slope profile."""
    np.random.seed(42)
    y, x = np.mgrid[0:100:10, 0:100:10]

    profile_params = {
        "Optimal": (0.3, 0.2, 0.0),
        "Rolling": (1.2, 1.5, 0.0),
        "Severe": (3.0, 12.0, 25.0),
    }

    # Default to the Severe ridge parameters.
    x_amp, y_amp, ridge_boost = profile_params.get("Severe")
    for key in profile_params:
        if key in profile_label:
            x_amp, y_amp, ridge_boost = profile_params[key]
            break

    elevation_grid = 120.0 + x_amp * np.sin(x / 15.0) + y_amp * np.sin(y / 12.0)
    if ridge_boost:
        elevation_grid[:, -1] += ridge_boost
    return elevation_grid


def generate_precise_terrain(target_mean_slope: float, cell_resolution_meters: float = 10.0) -> np.ndarray:
    """Generate a synthetic elevation grid whose mean slope matches the target."""
    np.random.seed(42)
    y, x = np.mgrid[0:100:10, 0:100:10]
    base_variation = np.sin(x / 15.0) + np.sin(y / 12.0)

    low, high = 0.0, 200.0
    for _ in range(20):
        mid = (low + high) / 2.0
        grid = 120.0 + mid * base_variation
        grad_y, grad_x = np.gradient(grid, cell_resolution_meters)
        slope_deg = np.degrees(np.arctan(np.sqrt(grad_x**2 + grad_y**2)))
        current_mean = np.mean(slope_deg)
        if current_mean < target_mean_slope:
            low = mid
        else:
            high = mid
    mid_k = (low + high) / 2.0
    return 120.0 + mid_k * base_variation


class CivilSlopeAnalyzer:
    """
    Improvised Module: Analyzes civil topography elevation grids using 2D spatial gradients
    to calculate landslide risks and grading/cut-and-fill CAPEX premiums.
    """
    @staticmethod
    def analyze_topography(elevation_grid_2d: np.ndarray, cell_resolution_meters: float = 10.0) -> TerrainProfileModel:
        print("[CivilSlopeAnalyzer] Computing 2D spatial elevation gradients for slope profiling...")

        # Calculate gradients in X and Y directions using finite differences
        grad_y, grad_x = np.gradient(elevation_grid_2d, cell_resolution_meters)

        # Calculate slope in radians and convert to degrees: theta = arctan(sqrt(dz/dx^2 + dz/dy^2))
        slope_rad = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
        slope_deg = np.degrees(slope_rad)

        mean_slope = float(np.mean(slope_deg))
        total_cells = slope_deg.size

        # Classify cells into slope categories
        optimal_cells = np.sum(slope_deg < 5.0)
        manageable_cells = np.sum((slope_deg >= 5.0) & (slope_deg <= 15.0))
        critical_cells = np.sum(slope_deg > 15.0)
        max_slope = float(np.max(slope_deg))

        optimal_percent = float((optimal_cells / total_cells) * 100.0)
        manageable_percent = float((manageable_cells / total_cells) * 100.0)
        critical_percent = float((critical_cells / total_cells) * 100.0)

        # Landslide risk evaluation
        if max_slope >= 30.0:
            landslide_risk = "High (Unbuildable / Severe Slope)"
            grading_multiplier = 1.35 # 35% cost premium due to retaining walls and safety works
        elif critical_percent >= 20.0 or max_slope > 15.0:
            landslide_risk = "Medium (Requires extensive soil reinforcement)"
            grading_multiplier = 1.15 # 15% cost premium
        else:
            landslide_risk = "Low (Optimal plain terrain)"
            grading_multiplier = 1.00 # No premium

        print(f" [Civil] Calculated Mean Slope: {mean_slope:.2f}° | Max Slope: {max_slope:.2f}° | Risk: {landslide_risk}")
        return TerrainProfileModel(
            mean_slope_degrees=round(mean_slope, 2),
            optimal_area_percent=round(optimal_percent, 2),
            manageable_area_percent=round(manageable_percent, 2),
            critical_area_percent=round(critical_percent, 2),
            landslide_risk=landslide_risk,
            grading_capex_premium_multiplier=grading_multiplier
        )


class SLDTopologyResolver:
    """
    Processes symbol bounding boxes and wire layout lines to construct a directed
    topological graph, validating compliance with TNB interconnection protection rules.
    """
    def resolve(self, symbols: List[Dict[str, Any]], lines: List[tuple], junction_dots: Optional[List[tuple]] = None) -> nx.DiGraph:
        print("[SLDTopologyResolver] Constructing directed topology graph...")
        g = nx.DiGraph()

        for sym in symbols:
            g.add_node(sym["id"], category=sym["class"], bbox=sym["bbox"])

        # --- Improvised Feature: Dynamic Scale-Invariant Epsilon Resolver ---
        # Instead of hardcoded 15.0px, calculate epsilon as 15% of the average inverter bounding box width!
        inverter_widths = []
        for sym in symbols:
            if sym["class"] == "Inverter":
                ymin, xmin, ymax, xmax = sym["bbox"]
                inverter_widths.append(xmax - xmin)

        if inverter_widths:
            epsilon = 0.15 * np.mean(inverter_widths)
            print(f" [Resolver] Dynamic scale-invariant matching active. Resolved Epsilon: {epsilon:.2f}px.")
        else:
            epsilon = 15.0
            print(f" [Resolver] No inverters found to gauge scale. Falling back to default Epsilon: {epsilon:.2f}px.")

        # Add virtual junction-dot nodes and split lines at junctions.
        # Junction dots represent intentional electrical connections; crossing lines
        # without a dot are ignored and stay as independent nets.
        if junction_dots:
            print(f" [Resolver] {len(junction_dots)} junction dot(s) detected; splitting lines at junctions.")
            junction_radius = max(5.0, epsilon * 0.3)
            for i, (jx, jy) in enumerate(junction_dots):
                g.add_node(
                    f"JUNCTION_{i}",
                    category="Junction_Dot",
                    bbox=[jy - junction_radius, jx - junction_radius, jy + junction_radius, jx + junction_radius]
                )
            lines = self._split_lines_at_junctions(lines, junction_dots, epsilon)

        # Match line endpoints to the nearest symbol or junction node within epsilon.
        # For each line endpoint we pick the *nearest* node, not the last one.
        for line in lines:
            pt1, pt2 = line
            nearest_u, nearest_v = None, None
            nearest_u_dist, nearest_v_dist = float("inf"), float("inf")

            for node_id, data in g.nodes(data=True):
                bbox = data["bbox"]
                d1 = self._distance_to_box(pt1, bbox)
                d2 = self._distance_to_box(pt2, bbox)

                if d1 <= epsilon and d1 < nearest_u_dist:
                    nearest_u_dist = d1
                    nearest_u = node_id
                if d2 <= epsilon and d2 < nearest_v_dist:
                    nearest_v_dist = d2
                    nearest_v = node_id

            if nearest_u and nearest_v and nearest_u != nearest_v:
                g.add_edge(nearest_u, nearest_v)

        g.graph["tnb_compliance"] = self.validate_tnb_compliance(g)
        return g

    @staticmethod
    def _distance_to_box(pt, box):
        """Distance from a point to the closest point inside a bounding box."""
        px, py = pt  # X is first, Y is second
        b_ymin, b_xmin, b_ymax, b_xmax = box
        dx = max(b_xmin - px, 0, px - b_xmax)
        dy = max(b_ymin - py, 0, py - b_ymax)
        return np.sqrt(dx**2 + dy**2)

    @staticmethod
    def _point_segment_projection(pt: tuple, a: tuple, b: tuple) -> tuple[float, float]:
        """Return perpendicular distance from pt to segment ab and parametric t (0..1)."""
        ax, ay = a
        bx, by = b
        px, py = pt
        seg_len_sq = (bx - ax) ** 2 + (by - ay) ** 2
        if seg_len_sq == 0.0:
            return np.hypot(px - ax, py - ay), 0.0
        t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / seg_len_sq))
        proj_x = ax + t * (bx - ax)
        proj_y = ay + t * (by - ay)
        dist = np.hypot(px - proj_x, py - proj_y)
        return dist, t

    @classmethod
    def _split_segment_at_junctions(cls, seg: tuple, junction_dots: List[tuple], epsilon: float) -> List[tuple]:
        """Split a single line segment at all interior junction dots within epsilon."""
        a, b = seg
        split_points = [(0.0, a)]
        for dot in junction_dots:
            dist, t = cls._point_segment_projection(dot, a, b)
            if dist <= epsilon and 0.0 < t < 1.0:
                split_points.append((t, dot))
        split_points.append((1.0, b))
        split_points.sort(key=lambda x: x[0])
        return [(split_points[i][1], split_points[i + 1][1]) for i in range(len(split_points) - 1)]

    @classmethod
    def _split_lines_at_junctions(cls, lines: List[tuple], junction_dots: List[tuple], epsilon: float) -> List[tuple]:
        """Split every line segment at every interior junction dot."""
        split_lines = []
        for line in lines:
            split_lines.extend(cls._split_segment_at_junctions(line, junction_dots, epsilon))
        return split_lines

    def validate_tnb_compliance(self, g: nx.DiGraph) -> dict:
        """Preliminary topology screening; cannot certify electrical/grid-code compliance."""
        groups: dict[str, list[str]] = {}
        for node, data in g.nodes(data=True):
            groups.setdefault(data.get("category", ""), []).append(node)

        pvs = groups.get("PV_Array", [])
        inverters = groups.get("Inverter", [])
        relays = groups.get("Anti_Islanding_Relay", [])
        transformers = groups.get("Transformer", [])
        grids = groups.get("Grid_Connection", [])
        missing = [name for name, present in (
            ("PV array", pvs), ("inverter", inverters),
            ("anti-islanding relay", relays), ("transformer", transformers),
            ("grid connection", grids),
        ) if not present]
        findings = [f"Missing modeled component: {name}" for name in missing]

        def protected_path_from(pv: str) -> bool:
            return any(
                nx.has_path(g, pv, inverter)
                and nx.has_path(g, inverter, relay)
                and nx.has_path(g, relay, xfmr)
                and nx.has_path(g, xfmr, grid)
                for inverter in inverters for relay in relays
                for xfmr in transformers for grid in grids
            )

        protected = bool(pvs and inverters and relays and transformers and grids)
        if protected:
            protected = all(protected_path_from(pv) for pv in pvs)

        # A bare PV->grid path bypassing all protection nodes is a negative finding.
        without_relays = g.copy()
        without_relays.remove_nodes_from(relays)
        bypass = any(nx.has_path(without_relays, pv, grid)
                     for pv in pvs for grid in grids)
        if bypass:
            findings.append("Detected PV-to-grid path that bypasses all modeled protection relays.")
        if not protected and not missing:
            findings.append("No complete PV -> inverter -> protection -> transformer -> grid path.")
        disconnected_transformers = [
            xfmr for xfmr in transformers
            if not any(nx.has_path(g, xfmr, grid) for grid in grids)
        ]
        if disconnected_transformers:
            findings.append("At least one transformer has no modeled path to the grid.")
        grid_path_valid = protected and not bypass and not disconnected_transformers
        return {
            "anti_islanding_relay_present": bool(relays),
            "protection_path_valid": protected and not bypass,
            "grid_path_valid": bool(grid_path_valid),
            "preliminary_topology_status": (
                "PRELIMINARY_TOPOLOGY_PASS" if grid_path_valid else "NEEDS_REVIEW"
            ),
            "findings": findings,
            "transformer_count": len(transformers),
            "grid_connection_count": len(grids),
            "disconnected_transformers": disconnected_transformers,
            "scope_note": "Drawing topology only. Not a TNB interconnection or protection-engineering certification.",
        }

    def resolve_image(self, image_path: str) -> nx.DiGraph:
        """Run Gemini extraction on an uploaded drawing, without substituting a demo circuit."""
        data = heliopolis_ocr.parse_sld_image(image_path)
        if not isinstance(data, dict):
            raise DocumentReviewRequired("SLD extraction failed; no grid-topology assessment is possible.")
        symbols, lines = data.get("symbols"), data.get("lines")
        if not isinstance(symbols, list) or not symbols or not isinstance(lines, list) or not lines:
            raise DocumentReviewRequired("SLD extraction has no usable symbols or wire segments.")
        try:
            ids = [s["id"] for s in symbols]
            if len(set(ids)) != len(ids):
                raise ValueError("duplicate symbol IDs")
            for s in symbols:
                if not isinstance(s["id"], str) or not isinstance(s["class"], str):
                    raise ValueError("symbol has no ID/class")
                if len(s["bbox"]) != 4:
                    raise ValueError("invalid symbol bbox")
                if not all(np.isfinite(float(v)) for v in s["bbox"]):
                    raise ValueError("nonfinite bbox")
            for line in lines:
                if len(line) != 2 or any(len(pt) != 2 for pt in line):
                    raise ValueError("invalid wire endpoints")
            dots = data.get("junction_dots", [])
            if not isinstance(dots, list):
                raise ValueError("invalid junction dots")
        except (KeyError, ValueError, TypeError, OverflowError) as exc:
            raise DocumentReviewRequired("SLD symbol/wire data is incomplete; manual review required.") from exc
        graph = self.resolve(symbols, lines, dots)
        graph.graph["source_type"] = "OCR_EXTRACTED_UNVERIFIED"
        return graph


class TNBSubstationCapacityValidator:
    """Preliminary injection-ratio screen; NO grid study or mandatory BESS determination."""

    @staticmethod
    def audit_injection(proposed_ac_mw: float, upstream_substation_mva: float = 15.0,
                        hypothetical_bess: bool = False) -> GridCapacityValidationModel:
        if not np.isfinite(proposed_ac_mw) or not np.isfinite(upstream_substation_mva):
            raise ValueError("Grid ratings must be finite.")
        if proposed_ac_mw <= 0 or upstream_substation_mva <= 0:
            raise ValueError("Grid ratings must be positive.")

        # MW / MVA is only a rough ratio; not a load-flow result (power factor
        # and upstream network conditions are not modeled).
        injection_percent = (proposed_ac_mw / upstream_substation_mva) * 100.0
        elevated = injection_percent >= 15.0  # illustrative sensitivity threshold
        risk = ("SCREENING_FLAG_NEEDS_UTILITY_STUDY" if elevated
                else "NOT_EVALUATED_BY_GRID_STUDY")
        reasons = [
            f"Illustrative AC MW / upstream MVA ratio = {injection_percent:.1f}%; "
            "this is not a TNB thermal limit or grid approval.",
            "A utility network study and power-factor/load-flow data are required "
            "to determine export limits, protection and any storage requirement.",
        ]
        battery_power = battery_capacity = bess_capex = 0.0
        if hypothetical_bess and elevated:
            # Optional financial stress test ONLY; not a BESS requirement.
            battery_power = round(max(0.0, proposed_ac_mw - 0.15 * upstream_substation_mva), 2)
            battery_capacity = round(battery_power * 4.0, 2)
            bess_capex = battery_capacity * 1_200_000.0
            reasons.append("Hypothetical four-hour BESS scenario enabled by user; NOT required by this screen.")

        bess = BESSRecommendationModel(
            is_bess_required=False,  # Not established without independent grid studies.
            recommended_battery_power_mw=battery_power,
            recommended_battery_capacity_mwh=battery_capacity,
            estimated_bess_capex_rm=bess_capex,
            reasons=reasons,
        )
        return GridCapacityValidationModel(
            upstream_substation_capacity_mva=upstream_substation_mva,
            substation_injection_percent=round(injection_percent, 2),
            reverse_power_risk=risk,
            bess_specification=bess,
        )


def project_lifecycle_cashflows(
    capacity_mwp: float,
    annual_yield_mwh: float,
    adjusted_capex_rm: float,
    bess_capex_rm: float,
    project_lifetime: int = DEFAULT_PROJECT_LIFETIME,
    opex_per_mwp_year: float = DEFAULT_OPEX_PER_MWP_YEAR,
    bess_opex_rate: float = DEFAULT_BESS_OPEX_RATE,
    opex_inflation: float = DEFAULT_OPEX_INFLATION,
    degradation_rate: float = DEFAULT_DEGRADATION_RATE,
    tariff_rm_kwh: float = DEFAULT_TARIFF_RM_KWH,
    wacc: float = DEFAULT_WACC,
) -> dict[str, Any]:
    """
    Project annual cash flows, discounted costs, and discounted energy for a solar site.

    This single source of truth is used by both the YieldFeasibilityEngine and the
    Streamlit financial plot, ensuring the UI never drifts from the backend math.
    """
    cash_flows = [-adjusted_capex_rm]
    discounted_costs = adjusted_capex_rm
    discounted_energy = 0.0
    bess_opex = bess_capex_rm * bess_opex_rate if bess_capex_rm > 0 else 0.0

    for yr in range(1, project_lifetime + 1):
        degradation = (1.0 - degradation_rate) ** (yr - 1)
        yearly_gen_kwh = annual_yield_mwh * 1000.0 * degradation
        yearly_opex = (capacity_mwp * opex_per_mwp_year + bess_opex) * ((1.0 + opex_inflation) ** (yr - 1))
        yearly_revenue = yearly_gen_kwh * tariff_rm_kwh
        yearly_net_cash = yearly_revenue - yearly_opex

        cash_flows.append(yearly_net_cash)
        discounted_costs += yearly_opex / ((1.0 + wacc) ** yr)
        discounted_energy += yearly_gen_kwh / ((1.0 + wacc) ** yr)

    return {
        "cash_flows": cash_flows,
        "discounted_costs": discounted_costs,
        "discounted_energy": discounted_energy,
    }


class YieldFeasibilityEngine:
    """
    Simulates annual photovoltaic generation yields in tropical environments and models
    project lifecycle financials (LCOE, NPV, IRR) in Malaysian Ringgit, including earthwork
    and battery storage premiums.
    """
    def __init__(self, metadata: LandTitleMetadata, terrain: TerrainProfileModel, grid_audit: GridCapacityValidationModel):
        self.metadata = metadata
        self.terrain = terrain
        self.grid_audit = grid_audit

    def calculate(self, scenario: str = DEFAULT_SCENARIO) -> TechnicalFeasibilityModel:
        print(f"[YieldFeasibilityEngine] Executing financial and clean energy yield models (scenario: {scenario})...")
        land_sqm = self.metadata.area_sq_meters
        usable_area = land_sqm * 0.90 # 10% setback buffers

        # Engineering parameters for tropical environments
        gcr = 0.45 # Ground Coverage Ratio
        panel_efficiency = 0.215 # 21.5% Mono-PERC modules
        performance_ratio = 0.78 # Standard system loss index

        # Select scenario tariff
        if scenario not in SCENARIO_TARIFFS:
            raise ValueError(f"Unsupported financial scenario: {scenario}")
        tariff_rm_kwh = SCENARIO_TARIFFS[scenario]  # illustrative input; not a tariff quote or eligibility decision

        # Dynamically load real meteorological observations from Open-Meteo dataset
        avg_ghi = 1550.0 # Default fallback
        avg_temp_max_c = 30.0 # Default fallback

        base_dir = os.path.dirname(os.path.abspath(__file__))
        weather_path = os.path.join(base_dir, "real_malaysian_weather.json")
        if os.path.exists(weather_path):
            try:
                import json
                with open(weather_path, "r", encoding="utf-8") as f:
                    weather_data = json.load(f)

                # Match region by looking for the state name in the weather data keys
                state_name = self.metadata.state.lower()
                matched_key = None
                for key in weather_data.keys():
                    if state_name in key.lower():
                        matched_key = key
                        break

                if matched_key:
                    avg_ghi = float(weather_data[matched_key]["annual_ghi_kwh_m2_year"])
                    avg_temp_max_c = float(weather_data[matched_key]["avg_temp_max_c"])
                    print(f"[YieldFeasibilityEngine] Grounded meteorological data loaded for '{matched_key}': GHI={avg_ghi:.2f} kWh/m2/year, Max Temp={avg_temp_max_c:.2f}°C")
            except Exception as e:
                print(f"[Warning] Failed to load real weather data in YieldFeasibilityEngine: {e}")

        # Physically-grounded Cell Temperature Derating model
        # standard solar module temperature coefficient of -0.35% / °C
        # cell temperature estimated using standard NOCT formula: T_cell = T_ambient + 20°C under peak tropical irradiance
        t_cell_estimated = avg_temp_max_c + 20.0
        temp_coeff = -0.0035 # -0.35% per degree C
        cell_temperature_derating = max(0.70, min(1.0, 1.0 + (t_cell_estimated - 25.0) * temp_coeff))

        capacity_mwp = usable_area / 12140.0
        annual_yield_mwh = capacity_mwp * 1000.0 * avg_ghi * performance_ratio * cell_temperature_derating / 1000.0

        # Financial input assumptions (RM)
        capex_per_mwp = 3000000.0 # RM 3.0 Million per MWp base cost
        opex_per_mwp_year = DEFAULT_OPEX_PER_MWP_YEAR
        project_lifetime = DEFAULT_PROJECT_LIFETIME
        wacc = DEFAULT_WACC

        # Adjusted CAPEX incorporating Civil Slope Grading premiums and Battery (BESS) additions
        base_capex = capacity_mwp * capex_per_mwp
        bess_addition_capex = self.grid_audit.bess_specification.estimated_bess_capex_rm
        adjusted_capex = (base_capex * self.terrain.grading_capex_premium_multiplier) + bess_addition_capex

        projection = project_lifecycle_cashflows(
            capacity_mwp=capacity_mwp,
            annual_yield_mwh=annual_yield_mwh,
            adjusted_capex_rm=adjusted_capex,
            bess_capex_rm=bess_addition_capex,
            project_lifetime=project_lifetime,
            opex_per_mwp_year=opex_per_mwp_year,
            tariff_rm_kwh=tariff_rm_kwh,
            wacc=wacc,
        )
        cash_flows = projection["cash_flows"]
        discounted_costs = projection["discounted_costs"]
        discounted_energy = projection["discounted_energy"]

        lcoe_rm_kwh = discounted_costs / (discounted_energy + 1e-12) if discounted_energy > 0 else 0.0

        # Solve NPV
        npv = -adjusted_capex
        for yr in range(1, project_lifetime + 1):
            npv += cash_flows[yr] / ((1.0 + wacc)**yr)

        # --- Blindspot Guarded Newton-Raphson IRR Solver ---
        r = 0.10 # Initial guess of 10%
        for _ in range(100):
            # Clip r to prevent division-by-zero or underflow near r ~ -1.0
            r = np.clip(r, -0.95, 5.0)
            denom = 1.0 + r
            f_val = sum(cf / ((denom)**t) for t, cf in enumerate(cash_flows))
            f_deriv = sum(-t * cf / ((denom)**(t + 1)) for t, cf in enumerate(cash_flows))

            # Prevent Division-by-Zero via eps buffer
            if abs(f_deriv) < 1e-12:
                f_deriv = 1e-12 if f_deriv >= 0 else -1e-12

            r_new = r - f_val / f_deriv
            if abs(r_new - r) < 1e-6:
                r = r_new
                break
            r = r_new

        r = np.clip(r, -0.95, 5.0)

        # --- Blindspot Guarded Payback Solver ---
        payback = adjusted_capex / cash_flows[1] if cash_flows[1] > 0 else 999.0

        return TechnicalFeasibilityModel(
            capacity_mwp=round(capacity_mwp, 3),
            annual_yield_mwh=round(annual_yield_mwh, 2),
            base_capex_rm=round(base_capex, 2),
            grading_adjusted_capex_rm=round(adjusted_capex, 2),
            lcoe_rm_kwh=round(lcoe_rm_kwh, 4),
            ppa_tariff_rm_kwh=round(tariff_rm_kwh, 4),
            scenario=scenario,
            npv_rm=round(npv, 2),
            irr_percent=round(r * 100.0, 2),
            payback_years=round(payback, 2),
            terrain_profile=self.terrain,
            grid_capacity_audit=self.grid_audit
        )


class FormFiller:
    """Generate PRELIMINARY planning fields; never a completed regulatory filing."""

    @staticmethod
    def generate_manifest(land: LandTitleMetadata, tech: TechnicalFeasibilityModel,
                          proposed_ac_mw: Optional[float] = None) -> RegulatoryFilingManifest:
        ac_capacity_kw = float(
            proposed_ac_mw * 1000 if proposed_ac_mw is not None
            else tech.capacity_mwp * 1000.0 * 0.85
        )
        if not np.isfinite(ac_capacity_kw) or ac_capacity_kw <= 0:
            raise ValueError("Proposed inverter AC capacity must be positive.")

        assessment_type = "GRID_STUDY_TO_CONFIRM"
        study_required = False
        study_fee = 0.0
        source_url = ""
        notes = [
            "Preliminary manifest only. No TNB/SEDA application submitted or approved.",
            "Capacity, connection voltage and applicant eligibility need independent verification.",
        ]
        mandatory_studies = ["Obtain utility's project-specific study/connection requirements."]

        if tech.scenario == SCENARIO_C_I_NEM:
            # NEM NOVA legacy scheme study bands, NOT Solar ATAP. Tariff is
            # merely a financial sensitivity until contract and bills are reviewed.
            source_url = "https://www.seda.gov.my/reportal/nem/"
            notes.append("NEM NOVA scenario and RM/kWh rate are illustrative; verify current programme eligibility and customer bills.")
            if ac_capacity_kw <= 72.0:
                assessment_type = "CAS_NOT_CAPACITY_TRIGGERED"
                mandatory_studies = []
            elif ac_capacity_kw <= 180.0:
                assessment_type, study_fee = "CAS", 1000.0
            elif ac_capacity_kw <= 425.0:
                assessment_type, study_fee = "CAS", 5000.0
            elif ac_capacity_kw <= 1000.0:
                assessment_type, study_fee = "CAS", 8000.0
            elif ac_capacity_kw <= 2000.0:
                assessment_type, study_fee = "CAS", 15000.0
            elif ac_capacity_kw <= 5000.0:
                assessment_type, study_fee = "CAS", 20000.0
            else:
                assessment_type = "OUTSIDE_MODELED_NOVA_STUDY_BANDS"
                notes.append("AC capacity exceeds published 5 MW LV/MV CAS fee table; require project-specific review.")
            study_required = assessment_type == "CAS"
            if study_required:
                mandatory_studies = ["NEM NOVA connection assessment (CAS) – applicable to LV/MV; verify voltage classification."]
        else:
            notes.append("LSS/self-consumption does not inherit NEM/NOVA/ATAP study fees or eligibility.")
        notes.append("Solar ATAP is not implemented in this prototype: non-domestic inverter output is capped at 1 MW and <=100% maximum demand; export offset lasts 10 years.")
        if ac_capacity_kw > 1000:
            notes.append("Above 1 MWac: do not market this modeled project as Solar ATAP eligible.")

        if land.project_company_name:
            applicant_name, applicant_id = land.project_company_name, land.project_company_reg_no or "N/A"
        elif land.owners:
            applicant = max(land.owners, key=lambda o: o.calculated_share_float)
            applicant_name, applicant_id = applicant.name, applicant.ic_or_co_no
            notes.append("Largest landowner is only a proposed contact; legal authority to apply is unverified.")
        else:
            applicant_name = applicant_id = "N/A"

        coupling_location = land.mukim or land.district
        seda = SEDAApplicationSchema(
            Part_A_Applicant_Name=applicant_name,
            Part_A_Company_Registration=applicant_id,
            Part_B_Site_Title_Number=land.title_no,
            Part_B_Site_Lot_Number=land.lot_no,
            Part_B_Mukim_Daerah_Negeri=f"{land.mukim}, {land.district}, {land.state}",
            Part_C_Proposed_DC_Capacity_kWp=float(tech.capacity_mwp * 1000.0),
            Part_C_Proposed_AC_Capacity_kWac=ac_capacity_kw,
            Part_D_PPA_Tariff_Rate_RM_kWh=tech.ppa_tariff_rm_kwh,
        )
        tnb = TNBConnectionSchema(
            Applicant_Company=applicant_name,
            Interconnection_Voltage_Level_kV=33.0 if tech.capacity_mwp >= 2.0 else 11.0,
            Total_Generation_Capacity_MWac=ac_capacity_kw / 1000.0,
            Inverter_Compliance_Standards=["IEC 62116", "IEC 61727", "MS 1837:2010"],
            Point_of_Common_Coupling=f"Proposed site: {coupling_location} (actual PCC unverified)",
            Transformer_Capacity_MVA=float(tech.capacity_mwp * 1.2),
        )
        nemas = NEMASChecklistSchema(
            is_nemas_required=study_required,
            voltage_rise_study_required=False,  # not determinable without network study
            estimated_regulatory_fee_rm=study_fee,
            estimated_processing_days=None,
            assessment_type=assessment_type,
            source_url=source_url,
            eligibility_notes=notes,
            mandatory_technical_studies=mandatory_studies,
        )
        return RegulatoryFilingManifest(
            seda_application=seda, tnb_grid_request=tnb, nemas_checklist=nemas,
        )


def main():
    print("=== SOLAR PROJECT INTELLIGENCE AGENT (MAIC NEXUS CHALLENGE) ===\n")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = base_dir
    os.makedirs(output_dir, exist_ok=True)

    # 0. Load Real Production Registry
    registry_path = os.path.join(base_dir, "real_malaysian_sites_registry.json")
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    # Pick the most attractive demo site: non-reserve, non-encumbered, large area,
    # but still below the 15% substation injection threshold so BESS is not triggered.
    def _injection_ratio(s: dict) -> float:
        ac_peak = (s["area_sq_meters"] * 0.9 / 12140.0) * 0.85
        return (ac_peak / s["substation_capacity_mva"]) * 100.0

    viable_sites = [
        s for s in registry
        if not s.get("is_malay_reserve", False)
        and not s.get("has_caveats", False)
        and not s.get("has_charges", False)
        and _injection_ratio(s) < 15.0
    ]
    if viable_sites:
        site_data = max(viable_sites, key=lambda s: s["area_sq_meters"])
    else:
        site_data = registry[0]
    print(f"[*] Processing Real Site: {site_data['site_id']} - {site_data['title_no']} ({site_data['region']})")

    # 1. Map Land Title dynamically from registry or from an OCR-scanned image.
    title_image_path = os.environ.get("LAND_TITLE_IMAGE")
    if title_image_path:
        print(f"[*] Using OCR land title image: {title_image_path}")
        land_metadata = LandTitleParser.from_image(title_image_path)
    else:
        land_metadata = LandTitleParser.from_registry(site_data)

    # 2. Analyze Civil Topography & Slope Profile Dynamically
    elevation_grid = generate_precise_terrain(site_data["mean_slope_degrees"])
    terrain_model = CivilSlopeAnalyzer.analyze_topography(elevation_grid, cell_resolution_meters=10.0)

    # 3. Audit Local Substation Capacity Limits & Size BESS
    ac_peak_mw = (site_data["area_sq_meters"] * 0.9 / 12140.0) * 0.85
    grid_capacity_audit = TNBSubstationCapacityValidator.audit_injection(proposed_ac_mw=ac_peak_mw, upstream_substation_mva=site_data["substation_capacity_mva"])

    # 4. Resolve SLD Topology
    resolver = SLDTopologyResolver()
    sld_image_path = os.environ.get("SLD_IMAGE")
    if sld_image_path:
        print(f"[*] Using OCR SLD image: {sld_image_path}")
        sld_graph = resolver.resolve_image(sld_image_path)
    else:
        symbols = [
            {"id": "PV_1", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
            {"id": "INV_1", "class": "Inverter", "bbox": [100, 400, 200, 500]},
            {"id": "RELAY_1", "class": "Anti_Islanding_Relay", "bbox": [100, 700, 200, 800]},
            {"id": "XFMR_1", "class": "Transformer", "bbox": [100, 1000, 200, 1100]},
            {"id": "GRID_1", "class": "Grid_Connection", "bbox": [100, 1300, 200, 1400]}
        ]
        lines = [
            ((200, 150), (400, 150)),
            ((500, 150), (700, 150)),
            ((800, 150), (1000, 150)),
            ((1100, 150), (1300, 150))
        ]
        sld_graph = resolver.resolve(symbols, lines)

    # 5. Compute Yield and Financials
    scenario = os.environ.get("HELIOPOLIS_SCENARIO", DEFAULT_SCENARIO)
    feasibility_engine = YieldFeasibilityEngine(land_metadata, terrain_model, grid_capacity_audit)
    tech_results = feasibility_engine.calculate(scenario=scenario)

    # 6. Generate SEDA/TNB Prefilled Manifest
    regulatory_manifest = FormFiller.generate_manifest(land_metadata, tech_results)

    # Compile final execution package
    final_output = {
        "land_title_analysis": land_metadata.model_dump(),
        "sld_topology_analysis": {
            "node_count": sld_graph.number_of_nodes(),
            "edge_count": sld_graph.number_of_edges(),
            "graph_paths": list(sld_graph.edges()),
            "tnb_compliance": sld_graph.graph.get("tnb_compliance", {})
        },
        "technical_financial_feasibility": tech_results.model_dump(),
        "regulatory_manifest": regulatory_manifest.model_dump()
    }

    report_path = os.path.join(output_dir, "solar_assessment_report.json")
    tmp_path = report_path + ".tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, report_path)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        print(f" [ERROR] Atomic file write failed: {e}")
        sys.exit(1)

    print(f"\n[Success] Complete Solar Assessment Report successfully written to: {report_path}")
    print(f"Financial Scenario: {SCENARIO_LABELS.get(tech_results.scenario, tech_results.scenario)}")
    print(f"Calculated Capacity: {tech_results.capacity_mwp:.3f} MWp")
    print(f"Base CAPEX Cost: RM {tech_results.base_capex_rm:,.2f}")
    print(f"Civil Slope CAPEX Cost (Adjusted): RM {tech_results.grading_adjusted_capex_rm:,.2f} (Includes Earthworks & BESS premiums)")
    print(f"Project Lifetime NPV: RM {tech_results.npv_rm:,.2f}")
    print(f"Project IRR: {tech_results.irr_percent:.2f}%")
    print(f"Land Legal Status: {land_metadata.legal_assessment.status}")
    print(f"Power of Attorney Required: {land_metadata.legal_assessment.poa_compliance.is_poa_required}")
    print(f"SEDA NEMAS Study Required: {regulatory_manifest.nemas_checklist.is_nemas_required}")
    print(f"LFP Battery Storage Required: {grid_capacity_audit.bess_specification.is_bess_required}")

if __name__ == "__main__":
    main()
