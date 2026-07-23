"""Pure backend logic, deterministic helpers, and assessment orchestration."""

import re
import numpy as np

from solar_agent import (
    LandTitleParser,
    CivilSlopeAnalyzer,
    TNBSubstationCapacityValidator,
    SLDTopologyResolver,
    YieldFeasibilityEngine,
    FormFiller,
    OwnerModel,
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


def deterministic_hash(string_val: str) -> int:
    """Return a deterministic 32-bit hash for a string."""
    h = 0
    for char in string_val:
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    return h


def generate_co_owners(count: int, site_id: str) -> list:
    """Generate a deterministic list of co-owner dicts for a site."""
    np.random.seed(sum(ord(c) for c in site_id))
    first_names = ["Ahmad", "Mohamad", "Siti", "Tan", "Lim", "Lee", "Ramasamy", "Muthu", "Karthik", "Abdul", "Wan", "Che", "Chong"]
    last_names = ["Bin Ismail", "Binti Ali", "Bin Ahmad", "Kah Seng", "Wei", "Meng", "Anak Nysem", "Bin Kassim", "Binti Hassan", "a/l Subramaniam", "a/p Devian"]

    owners = []

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

    for i in range(count):
        share_str = f"{shares[i]}/120"

        if i == 0 and count >= 3:
            name = "Solarvest Development Sdn Bhd"
            ic_co = "1234567-U"
        else:
            fn = first_names[deterministic_hash(f"fn_{i}_{site_id}") % len(first_names)]
            ln = last_names[deterministic_hash(f"ln_{i}_{site_id}") % len(last_names)]
            name = f"{fn} {ln}"

            birth_yr = deterministic_hash(f"yr_{i}_{site_id}") % 50 + 50
            birth_mo = deterministic_hash(f"mo_{i}_{site_id}") % 12 + 1
            birth_dy = deterministic_hash(f"dy_{i}_{site_id}") % 28 + 1
            state_code = deterministic_hash(f"st_{i}_{site_id}") % 14 + 1
            unique_code = deterministic_hash(f"un_{i}_{site_id}") % 9000 + 1000
            ic_co = f"{birth_yr:02d}{birth_mo:02d}{birth_dy:02d}-{state_code:02d}-{unique_code:d}"

        owners.append({
            "name": name,
            "id": ic_co,
            "share": share_str
        })

    return owners


def _imperial_string_to_parts(area_imperial: str) -> tuple[float, float, float]:
    """Parse an 'X Ekar Y Rood Z Pole' string into (acres, roods, poles)."""
    match = re.search(r"(\d+)\s*Ekar", area_imperial, re.IGNORECASE)
    acres = float(match.group(1)) if match else 0.0
    match = re.search(r"(\d+)\s*Rood", area_imperial, re.IGNORECASE)
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
):
    """Build a fully populated LandTitleMetadata object from raw form inputs or a scanned image."""
    if title_image_path:
        print("[app_logic] Building land metadata from OCR image...")
        land_meta = LandTitleParser.from_image(title_image_path)
        owner_models = land_meta.owners
        hectares = land_meta.area_hectares
        sq_meters = land_meta.area_sq_meters
        acres, roods, poles = _imperial_string_to_parts(land_meta.area_imperial)
    else:
        hectares, sq_meters = LandTitleParser.convert_imperial_to_metric(acres, roods, poles)

        owner_models = [
            OwnerModel(
                name=o["name"],
                ic_or_co_no=o["id"],
                share_fraction=o["share"],
                calculated_share_float=LandTitleParser.parse_fraction(o["share"])
            )
            for o in owners_list
        ]

        poa_model = LandTitleParser._compute_poa(owner_models)
        legal_assessment = LandTitleParser._compute_legal_assessment(
            zoning, caveats, charges, reserve, poa_model
        )

        # Start from the demo parser output so we inherit sensible district/mukim defaults.
        land_meta = LandTitleParser().parse("")
        land_meta.title_no = title_no
        land_meta.lot_no = lot_no
        land_meta.state = state
        land_meta.zoning = zoning
        land_meta.area_imperial = f"{int(acres)} Ekar {int(roods)} Rood {poles} Pole"
        land_meta.area_hectares = hectares
        land_meta.area_sq_meters = sq_meters
        land_meta.is_malay_reserve = reserve
        land_meta.has_caveats = caveats
        land_meta.has_charges = charges
        land_meta.owners = owner_models
        land_meta.legal_assessment = legal_assessment

    owner_rows_html = app_components.owner_rows_html(owner_models)
    return land_meta, hectares, sq_meters, acres, roods, poles, owner_rows_html


def compute_assessment(
    land_meta,
    slope_profile: str,
    ac_capacity: float,
    substation_mva: float,
    site_mode: str = "Standard Presets",
    has_relay: bool = True,
    is_xfmr_connected: bool = True,
    sld_image_path: str | None = None,
):
    """Run the full technical assessment pipeline and return a result dict."""
    # --- Civil Terrain Grid Generator ---
    if site_mode == "Real Malaysian Sites (500)":
        target_slope = parse_mean_slope(slope_profile)
        elevation_grid = generate_precise_terrain(target_slope)
    else:
        elevation_grid = _synthetic_elevation_grid(slope_profile)

    terrain_model = CivilSlopeAnalyzer.analyze_topography(elevation_grid, cell_resolution_meters=10.0)

    # --- Grid Battery Audit ---
    grid_audit = TNBSubstationCapacityValidator.audit_injection(
        proposed_ac_mw=ac_capacity,
        upstream_substation_mva=substation_mva
    )

    # --- Financial Feasibility ---
    feasibility = YieldFeasibilityEngine(
        metadata=land_meta,
        terrain=terrain_model,
        grid_audit=grid_audit
    ).calculate()

    # --- SLD Topology ---
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

    resolver = SLDTopologyResolver()
    if sld_image_path:
        print("[app_logic] Resolving SLD topology from OCR image...")
        sld_graph = resolver.resolve_image(sld_image_path)
    else:
        sld_graph = resolver.resolve(symbols, lines)

    # --- Regulatory Manifest ---
    manifest = FormFiller.generate_manifest(land=land_meta, tech=feasibility)

    return {
        "terrain_model": terrain_model,
        "grid_audit": grid_audit,
        "feasibility": feasibility,
        "sld_graph": sld_graph,
        "manifest": manifest,
    }
