"""Pure backend logic, deterministic helpers, and assessment orchestration."""

import re
import numpy as np

from solar_agent import (
    LandTitleParser,
    LandTitleMetadata,
    DocumentReviewRequired,
    CivilSlopeAnalyzer,
    TNBSubstationCapacityValidator,
    SLDTopologyResolver,
    YieldFeasibilityEngine,
    FormFiller,
    OwnerModel,
    project_lifecycle_cashflows,
    generate_precise_terrain,
    _synthetic_elevation_grid,
    deterministic_hash,
    generate_co_owners,
    DEFAULT_SCENARIO,
    SCENARIO_LABELS,
)
import app_components


def get_state_from_region(region_str: str) -> str:
    """Extract the Malaysian state from a region descriptor."""
    state_part = region_str.split("(")[0].strip()
    for s in ["Perak", "Kedah", "Kelantan", "Selangor", "Johor"]:
        if s.lower() in state_part.lower():
            return s
    return "Selangor"  # Fallback


def parse_mean_slope(profile_str: str) -> float:
    """Parse the mean slope in degrees from a slope-profile label."""
    match = re.search(r"([\d\.]+)\s*°", profile_str)
    if match:
        return float(match.group(1))
    if "Optimal" in profile_str:
        return 2.1
    if "Rolling" in profile_str:
        return 8.5
    return 37.7


def _sld_node_style(category: str, node_id: str) -> dict:
    """Return color, size and label for a node based on its SLD category."""
    styles = {
        "PV_Array": {"color": "#34d399", "size": 1500, "label": "PV Array"},
        "Inverter": {"color": "#60a5fa", "size": 1500, "label": "Inverter"},
        "Anti_Islanding_Relay": {"color": "#fbbf24", "size": 1800, "label": "Anti-Islanding Relay"},
        "Transformer": {"color": "#f87171", "size": 1500, "label": "Transformer"},
        "Grid_Connection": {"color": "#a78bfa", "size": 1500, "label": "TNB Grid"},
    }
    style = styles.get(category, {"color": "#9ca3af", "size": 1200, "label": ""}).copy()
    if style["label"]:
        style["label"] = f"{style['label']}\n({node_id})"
    else:
        style["label"] = node_id
    return style


def _imperial_string_to_parts(area_imperial: str) -> tuple[float, float, float]:
    """Parse an 'X Ekar Y Rood Z Pole' string into (acres, roods, poles)."""
    match = re.search(r"(\d+(?:\.\d+)?)\s*Ekar", area_imperial, re.IGNORECASE)
    acres = float(match.group(1)) if match else 0.0
    match = re.search(r"(\d+(?:\.\d+)?)\s*Rood", area_imperial, re.IGNORECASE)
    roods = float(match.group(1)) if match else 0.0
    match = re.search(r"([\d.]+)\s*Pole", area_imperial, re.IGNORECASE)
    poles = float(match.group(1)) if match else 0.0
    return acres, roods, poles


def build_land_metadata(
    title_no: str,
    lot_no: str,
    state: str,
    zoning: str,
    acres: float,
    roods: float,
    poles: float,
    caveats: bool,
    charges: bool,
    reserve: bool,
    owners_list: list,
    title_image_path: str | None = None,
    project_company_name: str = "",
    project_company_reg_no: str = "",
    source_type: str = "USER_ENTERED_UNVERIFIED",
):
    """Build metadata from a form or uploaded title without secretly inheriting a demo fixture."""
    if title_image_path:
        print("[app_logic] Building land metadata from OCR image...")
        land_meta = LandTitleParser.from_image(title_image_path)
        # These two inputs are entered by the user, not inferred from the scan.
        land_meta.project_company_name = project_company_name
        land_meta.project_company_reg_no = project_company_reg_no
        owner_models = land_meta.owners
        hectares = land_meta.area_hectares
        sq_meters = land_meta.area_sq_meters
        acres, roods, poles = _imperial_string_to_parts(land_meta.area_imperial)
    else:
        hectares, sq_meters = LandTitleParser.convert_imperial_to_metric(acres, roods, poles)

        if not owners_list:
            raise DocumentReviewRequired("At least one registered proprietor must be recorded.")
        try:
            owner_models = [
                OwnerModel(
                    name=owner["name"],
                    ic_or_co_no=owner["id"],
                    share_fraction=owner["share"],
                    calculated_share_float=LandTitleParser.parse_fraction_strict(owner["share"]),
                )
                for owner in owners_list
            ]
        except (KeyError, TypeError, ValueError) as exc:
            raise DocumentReviewRequired("Owner records or shares are incomplete or invalid.") from exc
        if abs(sum(o.calculated_share_float for o in owner_models) - 1.0) > 0.001:
            raise DocumentReviewRequired("Owner fractions do not sum to 100%; verify source records.")
        poa_model = LandTitleParser._compute_poa(owner_models)
        legal_assessment = LandTitleParser._compute_legal_assessment(
            zoning, caveats, charges, reserve, poa_model
        )
        land_meta = LandTitleMetadata(
            source_type=source_type,
            review_status="NEEDS_LEGAL_REVIEW",
            title_no=title_no,
            lot_no=lot_no,
            state=state,
            district="",
            mukim="",
            zoning=zoning,
            area_imperial=f"{acres:g} Ekar {roods:g} Rood {poles:g} Pole",
            area_hectares=hectares,
            area_sq_meters=sq_meters,
            owners=owner_models,
            project_company_name=project_company_name,
            project_company_reg_no=project_company_reg_no,
            has_caveats=caveats,
            has_charges=charges,
            is_malay_reserve=reserve,
            legal_assessment=legal_assessment,
        )

    owner_rows_html = app_components.owner_rows_html(owner_models)
    return land_meta, hectares, sq_meters, acres, roods, poles, owner_rows_html


def build_demo_sld(has_relay: bool = True, is_xfmr_connected: bool = True):
    """Construct an explicit synthetic SLD fixture for judge/demo toggles only."""
    symbols = [
        {"id": "PV_1", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
        {"id": "INV_1", "class": "Inverter", "bbox": [100, 400, 200, 500]},
        {"id": "XFMR_1", "class": "Transformer", "bbox": [100, 1000, 200, 1100]},
        {"id": "GRID_1", "class": "Grid_Connection", "bbox": [100, 1300, 200, 1400]}
    ]
    if has_relay:
        symbols.append({"id": "RELAY_1", "class": "Anti_Islanding_Relay", "bbox": [100, 700, 200, 800]})

    lines = [
        ((200, 150), (400, 150)),  # PV to Inverter
    ]
    if has_relay:
        lines.append(((500, 150), (700, 150)))  # Inverter to Relay
        if is_xfmr_connected:
            lines.append(((800, 150), (1000, 150)))  # Relay to Transformer
            lines.append(((1100, 150), (1300, 150)))  # Transformer to Grid
        else:
            lines.append(((1100, 150), (1200, 150)))  # Broken wire
    else:
        if is_xfmr_connected:
            lines.append(((500, 150), (1000, 150)))  # Inverter to Transformer directly
            lines.append(((1100, 150), (1300, 150)))  # Transformer to Grid

    graph = SLDTopologyResolver().resolve(symbols, lines)
    graph.graph["source_type"] = "SYNTHETIC_DEMO"
    return graph


def compute_assessment(
    land_meta,
    slope_profile: str,
    ac_capacity: float,
    substation_mva: float,
    site_mode: str = "Standard Presets",
    has_relay: bool = True,
    is_xfmr_connected: bool = True,
    sld_image_path: str | None = None,
    scenario: str = DEFAULT_SCENARIO,
    voltage_class: str = "UNKNOWN",
    maximum_demand_kw: float | None = None,
    hypothetical_bess: bool = False,
):
    """Run the full technical assessment pipeline and return a result dict."""
    # --- Civil Terrain Grid Generator (synthetic terrain until real DEM is supplied) ---
    if site_mode == "Synthetic Malaysian Sites (500)":
        target_slope = parse_mean_slope(slope_profile)
        elevation_grid = generate_precise_terrain(target_slope)
    else:
        elevation_grid = _synthetic_elevation_grid(slope_profile)

    terrain_model = CivilSlopeAnalyzer.analyze_topography(elevation_grid, cell_resolution_meters=10.0)

    # --- Grid Battery Audit ---
    grid_audit = TNBSubstationCapacityValidator.audit_injection(
        proposed_ac_mw=ac_capacity,
        upstream_substation_mva=substation_mva,
        hypothetical_bess=hypothetical_bess,
    )

    # --- Financial Feasibility ---
    feasibility = YieldFeasibilityEngine(
        metadata=land_meta,
        terrain=terrain_model,
        grid_audit=grid_audit
    ).calculate(scenario=scenario)

    # Uploaded OCR graph is analyzed once; a synthetic fixture needs no cloud call.
    if sld_image_path:
        print("[app_logic] Resolving SLD topology from uploaded OCR image...")
        sld_graph = SLDTopologyResolver().resolve_image(sld_image_path)
    else:
        sld_graph = build_demo_sld(has_relay, is_xfmr_connected)

    # --- Regulatory Manifest ---
    manifest = FormFiller.generate_manifest(
        land=land_meta, tech=feasibility, proposed_ac_mw=ac_capacity,
        voltage_class=voltage_class, maximum_demand_kw=maximum_demand_kw,
    )

    return {
        "data_provenance": {"land": land_meta.source_type, "terrain": "SYNTHETIC_TERRAIN", "sld": sld_graph.graph.get("source_type", "SYNTHETIC_DEMO")},
        "assessment_scope": "PRELIMINARY_SCREENING_ONLY",
        "terrain_model": terrain_model,
        "grid_audit": grid_audit,
        "feasibility": feasibility,
        "sld_graph": sld_graph,
        "manifest": manifest,
    }


def validate_inputs(
    acres: float,
    roods: float,
    poles: float,
    ac_capacity: float,
    substation_mva: float,
    state: str,
    title_no: str,
    lot_no: str,
    owners_list: list,
) -> list[str]:
    """Return a list of human-readable validation errors, or an empty list if valid."""
    errors: list[str] = []
    if not all(np.isfinite(v) for v in (acres, roods, poles, ac_capacity, substation_mva)):
        return ["All area, AC capacity, and substation input values must be finite."]
    if acres < 0 or not 0 <= roods < 4 or not 0 <= poles < 40:
        errors.append("Use non-negative acres, 0–3 roods and 0–39.999 poles.")
    hectares, sq_meters = LandTitleParser.convert_imperial_to_metric(acres, roods, poles)
    if sq_meters <= 1000.0:
        errors.append("Land area is too small for a utility or C&I solar site (minimum ~1,000 m²).")
    if ac_capacity <= 0.0:
        errors.append("Proposed AC capacity must be greater than 0 MWac.")
    if ac_capacity > 1000.0:
        errors.append("Proposed AC capacity exceeds 1,000 MWac — please check the unit is MWac.")
    if substation_mva <= 0.0:
        errors.append("Upstream substation capacity must be greater than 0 MVA.")
    if not state or state.strip() == "":
        errors.append("State is required.")
    if not title_no or not title_no.strip():
        errors.append("Title No is required.")
    if not lot_no or not lot_no.strip():
        errors.append("Lot No is required.")
    if not owners_list:
        errors.append("At least one landowner is required.")
    else:
        try:
            shares = [LandTitleParser.parse_fraction_strict(o["share"]) for o in owners_list]
            if abs(sum(shares) - 1.0) > 0.001:
                errors.append("Registered owner fractions must sum to 100%.")
        except (KeyError, TypeError, ValueError):
            errors.append("Owner share fractions must be valid (e.g. 1/2).")
    return errors
