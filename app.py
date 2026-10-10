import os
import sys
import json
import tempfile
from html import escape as html_escape
import numpy as np
import networkx as nx
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Ensure current folder is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app_config import (
    PAGE_CONFIG,
    get_css,
    STATE_LIST,
    ZONING_LIST,
    SLOPE_PROFILES,
    SAMPLE_OWNERS,
)
from app_components import clean_html_markdown, metric_card, status_badge
from solar_agent import DocumentReviewRequired
import heliopolis_ocr
from app_logic import (
    get_state_from_region,
    generate_co_owners,
    build_land_metadata,
    compute_assessment,
    build_demo_sld,
    project_lifecycle_cashflows,
    _sld_node_style,
    DEFAULT_SCENARIO,
    SCENARIO_LABELS,
    validate_inputs,
)

def stop_with_review(reason: str, evidence_type: str) -> None:
    """Fail closed and let a reviewer download the issue instead of a fake approval."""
    st.error(f"{evidence_type} requires manual review: {reason}")
    report = {
        "assessment_status": "NEEDS_REVIEW",
        "scope": "NO_LEGAL_GRID_OR_FINANCIAL_CLEARANCE",
        "evidence_type": evidence_type,
        "source_type": "UPLOADED_UNVERIFIED",
        "reason": str(reason),
        "regulatory_approval": False,
        "verified_site_result": None,
    }
    st.download_button(
        label="Download review-required report (JSON)",
        data=json.dumps(report, indent=2),
        file_name="heliopolis_needs_review.json",
        mime="application/json",
    )
    st.stop()


# --- Page Setup ---
st.set_page_config(**PAGE_CONFIG)

# --- Theme Toggle Pattern ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


IS_DARK = st.session_state.theme == "dark"

# --- Custom CSS ---
st.markdown(get_css(IS_DARK), unsafe_allow_html=True)

# --- Header ---
head_left, head_right = st.columns([10, 2])
with head_left:
    st.markdown("""
    <div class="brand">
        <span class="brand-icon">◆</span>
        <span class="brand-name">Heliopolis-AI</span>
        <span class="brand-badge">Solar Project Intelligence</span>
    </div>
    <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: -0.2rem; margin-bottom: 1.25rem;">
        AI-assisted Preliminary Solar Site Screening (Malaysia) · Not a legal or grid-connection approval
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True, key="theme_toggle_btn")

# --- Preset Configurations ---
presets = {
    "Perak Site (Default High Slope)": {
        "title": "GRN 45293", "lot": "Lot 8192", "state": "Perak", "district": "Larut dan Matang",
        "acres": 12.0, "roods": 2.0, "poles": 15.0, "zoning": "Pertanian",
        "caveats": True, "charges": True, "reserve": False, "slope_profile": "Severe Ridge (37.7° mean)",
        "ac_capacity": 3.21, "substation_mva": 15.0
    },
    "Kedah Plain (Flat - Optimal)": {
        "title": "GRN 82914", "lot": "Lot 1042", "state": "Kedah", "district": "Kubang Pasu",
        "acres": 25.0, "roods": 0.0, "poles": 0.0, "zoning": "Pertanian",
        "caveats": False, "charges": False, "reserve": False, "slope_profile": "Optimal Flat Plain (2.1° mean)",
        "ac_capacity": 5.0, "substation_mva": 45.0
    },
    "Kelantan Reserve (Malay Reserve - Blocked)": {
        "title": "GRN 11043", "lot": "Lot 3091", "state": "Kelantan", "district": "Kota Bharu",
        "acres": 8.0, "roods": 1.0, "poles": 10.0, "zoning": "Pertanian",
        "caveats": False, "charges": False, "reserve": True, "slope_profile": "Rolling Hills (8.5° mean)",
        "ac_capacity": 1.5, "substation_mva": 15.0
    }
}

# --- Load Real Malaysian Sites ---
real_sites = []
real_sites_path = os.path.join(os.path.dirname(__file__), "real_malaysian_sites_registry.json")
if os.path.exists(real_sites_path):
    try:
        with open(real_sites_path, "r", encoding="utf-8") as f:
            real_sites = json.load(f)
    except Exception as e:
        print(f"Error loading real sites: {e}")

# Initialize session state keys if missing
if "prev_selected_mode" not in st.session_state:
    st.session_state.prev_selected_mode = None
if "prev_selected_preset" not in st.session_state:
    st.session_state.prev_selected_preset = None
if "prev_selected_site" not in st.session_state:
    st.session_state.prev_selected_site = None

# --- Sidebar Inputs ---
with st.sidebar:
    st.markdown('<div class="card-title">Scenario Control Panel</div>', unsafe_allow_html=True)
    st.caption("Presets, site registry and terrain are synthetic demonstrations unless independent project evidence is supplied.")
    site_mode = st.radio("Selection Mode", ["Standard Presets", "Synthetic Malaysian Sites (500)"], horizontal=True, key="site_mode_selector")

    selected_preset = None
    selected_site = None

    if site_mode == "Standard Presets":
        selected_preset = st.selectbox("Load Site Preset", list(presets.keys()), key="preset_selector")
        preset_data = presets[selected_preset]

        # If selection mode or target changed, update inputs in session_state
        if st.session_state.prev_selected_mode != "Standard Presets" or st.session_state.prev_selected_preset != selected_preset:
            st.session_state.in_title = preset_data["title"]
            st.session_state.in_lot = preset_data["lot"]
            st.session_state.in_state = preset_data["state"]
            st.session_state.in_zoning = preset_data["zoning"]
            st.session_state.in_acres = float(preset_data["acres"])
            st.session_state.in_roods = float(preset_data["roods"])
            st.session_state.in_poles = float(preset_data["poles"])
            st.session_state.in_caveats = preset_data["caveats"]
            st.session_state.in_charges = preset_data["charges"]
            st.session_state.in_reserve = preset_data["reserve"]
            st.session_state.in_slope_profile = preset_data["slope_profile"]
            st.session_state.in_ac_capacity = float(preset_data["ac_capacity"])
            st.session_state.in_substation_mva = float(preset_data["substation_mva"])

            st.session_state.prev_selected_mode = "Standard Presets"
            st.session_state.prev_selected_preset = selected_preset
    else:
        regions = sorted(list(set(s["region"] for s in real_sites)))
        selected_region = st.selectbox("Filter Region", ["All Regions"] + regions, key="region_filter")

        if selected_region == "All Regions":
            filtered_sites = real_sites
        else:
            filtered_sites = [s for s in real_sites if s["region"] == selected_region]

        site_options = [f"{s['site_id']} - {s['region']} ({s['title_no']})" for s in filtered_sites]
        selected_site_str = st.selectbox("Select Synthetic Example Site", site_options, key="site_selector")

        if selected_site_str:
            selected_idx = site_options.index(selected_site_str)
            site_data = filtered_sites[selected_idx]

            # If selection mode or target changed, update inputs in session_state
            if st.session_state.prev_selected_mode != "Synthetic Malaysian Sites" or st.session_state.prev_selected_site != site_data["site_id"]:
                st.session_state.in_title = site_data["title_no"]
                st.session_state.in_lot = site_data["lot_no"]
                st.session_state.in_state = get_state_from_region(site_data["region"])
                st.session_state.in_zoning = site_data["zoning"]
                st.session_state.in_acres = float(round(site_data["area_sq_meters"] / 4046.8564, 2))
                st.session_state.in_roods = 0.0
                st.session_state.in_poles = 0.0
                st.session_state.in_caveats = site_data["has_caveats"]
                st.session_state.in_charges = site_data["has_charges"]
                st.session_state.in_reserve = site_data["is_malay_reserve"]

                slope_val = site_data["mean_slope_degrees"]
                if slope_val < 5.0:
                    st.session_state.in_slope_profile = f"Optimal Flat Plain ({slope_val:.2f}° mean)"
                elif slope_val <= 15.0:
                    st.session_state.in_slope_profile = f"Rolling Hills ({slope_val:.2f}° mean)"
                else:
                    st.session_state.in_slope_profile = f"Severe Ridge ({slope_val:.2f}° mean)"

                mwp_est = (site_data["area_sq_meters"] * 0.9) / 12140.0
                st.session_state.in_ac_capacity = float(round(mwp_est * 0.85, 2))
                st.session_state.in_substation_mva = float(site_data["substation_capacity_mva"])

                st.session_state.prev_selected_mode = "Synthetic Malaysian Sites"
                st.session_state.prev_selected_site = site_data["site_id"]

    st.markdown("---")
    st.markdown('<div class="card-title">Land Attributes</div>', unsafe_allow_html=True)
    in_title = st.text_input("Title No", value=st.session_state.get("in_title", "GRN 45293"))
    in_lot = st.text_input("Lot No", value=st.session_state.get("in_lot", "Lot 8192"))

    current_state = st.session_state.get("in_state", "Perak")
    state_list = STATE_LIST.copy()
    if current_state not in state_list:
        state_list.append(current_state)
    in_state = st.selectbox("State", state_list, index=state_list.index(current_state))

    current_zoning = st.session_state.get("in_zoning", "Pertanian")
    zoning_list = ZONING_LIST.copy()
    if current_zoning not in zoning_list:
        zoning_list.append(current_zoning)
    in_zoning = st.selectbox("Zoning (Kategori)", zoning_list, index=zoning_list.index(current_zoning))

    col_acres, col_roods, col_poles = st.columns(3)
    with col_acres:
        in_acres = st.number_input("Ekar (Acres)", value=st.session_state.get("in_acres", 12.0), step=1.0)
    with col_roods:
        in_roods = st.number_input("Rood", value=st.session_state.get("in_roods", 2.0), step=1.0)
    with col_poles:
        in_poles = st.number_input("Pole", value=st.session_state.get("in_poles", 15.0), step=1.0)

    st.markdown('<div class="card-title">Legal Restrictions</div>', unsafe_allow_html=True)
    in_caveats = st.checkbox("Active Private Caveat (Kaveat)", value=st.session_state.get("in_caveats", True))
    in_charges = st.checkbox("Active Bank Charge (Gadaian)", value=st.session_state.get("in_charges", True))
    in_reserve = st.checkbox("Malay Reserve Land (Rezab Melayu)", value=st.session_state.get("in_reserve", False))

    st.markdown('<div class="card-title">Project Company</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.5rem;">SEDA/TNB permits are filed by the project company, not the landowner.</div>', unsafe_allow_html=True)
    in_project_company_name = st.text_input("Applicant Company (optional; user-entered)", value=st.session_state.get("in_project_company_name", ""), placeholder="Enter only a verified applicant")
    in_project_company_reg = st.text_input("Company registration (optional)", value=st.session_state.get("in_project_company_reg", ""), placeholder="Do not invent an SSM number")

    st.markdown('<div class="card-title">Technical Specifications</div>', unsafe_allow_html=True)
    current_slope_profile = st.session_state.get("in_slope_profile", "Severe Ridge (37.7° mean)")
    slope_profiles_list = SLOPE_PROFILES.copy()
    if current_slope_profile not in slope_profiles_list:
        slope_profiles_list.append(current_slope_profile)
    in_slope_profile = st.selectbox("Terrain Slope Profile", slope_profiles_list, index=slope_profiles_list.index(current_slope_profile))

    in_ac_capacity = st.number_input("Proposed AC Capacity (MWac)", value=st.session_state.get("in_ac_capacity", 3.21), step=0.1)
    in_substation_mva = st.number_input("Assumed Upstream Substation Rating (MVA)", value=st.session_state.get("in_substation_mva", 15.0), step=1.0)
    in_voltage_class = st.selectbox(
        "Connection voltage class (user assumption)",
        ["UNKNOWN", "LV", "MV", "HV"],
        help="Do not infer the voltage class from PV system size. Unknown means no historical scheme-specific fee can be estimated.",
    )
    in_maximum_demand = st.number_input(
        "Provided Consumer Maximum Demand (kW; unverified, 0 = unknown)",
        value=0.0, min_value=0.0, step=10.0,
        help="ATAP non-domestic capacity cannot exceed 100% of MD or 1,000 kW. Unknown is not proof of eligibility.",
    )
    in_hypothetical_bess = st.checkbox(
        "Illustrative 4-hour BESS what-if (NOT a TNB requirement)", value=False
    )

    st.markdown('<div class="card-title">Financial Scenario</div>', unsafe_allow_html=True)
    scenario_options = list(SCENARIO_LABELS.values())
    scenario_keys = list(SCENARIO_LABELS.keys())
    current_scenario = st.session_state.get("in_scenario", DEFAULT_SCENARIO)
    if current_scenario not in scenario_keys:
        current_scenario = DEFAULT_SCENARIO
    in_scenario_label = st.selectbox(
        "Revenue Scenario",
        scenario_options,
        index=scenario_keys.index(current_scenario),
        help="All scenarios are illustrative. LSS PPA and C&I/NEM NOVA are distinct, and Solar ATAP eligibility/economics are not modeled.",
    )
    in_scenario = scenario_keys[scenario_options.index(in_scenario_label)]
    st.session_state["in_scenario"] = in_scenario

    st.markdown("---")
    st.markdown('<div class="card-title">Scanned Document OCR</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.5rem;">Upload images to run real Gemini OCR. Leave blank to use the form values above.</div>', unsafe_allow_html=True)
    title_image_file = st.file_uploader("Land Title Scan (PNG/JPG)", type=["png", "jpg", "jpeg"])
    sld_image_file = st.file_uploader("SLD Diagram Scan (PNG/JPG)", type=["png", "jpg", "jpeg"])
    st.caption(
        "Uploaded scans are sent to Google Gemini/Vertex AI for OCR. "
        "Real land titles may contain names and identification numbers. "
        "Do not upload real personal/confidential data without authorization."
    )
    allow_cloud_ocr = st.checkbox(
        "I have authorization to send these uploaded scans to the configured Google AI service.",
        value=False,
    )


if (title_image_file or sld_image_file) and not allow_cloud_ocr:
    st.warning("Uploaded scan NOT sent to Gemini: explicit document-transfer authorization is required.")
    st.stop()

# --- Compute Ownership Splits ---
if site_mode == "Synthetic Malaysian Sites (500)":
    active_site_id = st.session_state.get("prev_selected_site", "MY-SITE-0001")
    matching_site = next((s for s in real_sites if s["site_id"] == active_site_id), None)
    co_owners_cnt = matching_site["co_owners_count"] if matching_site else 5
    owners_list = generate_co_owners(co_owners_cnt, active_site_id)
else:
    owners_list = SAMPLE_OWNERS

# --- Validate User Inputs ---
validation_errors = validate_inputs(
    acres=in_acres,
    roods=in_roods,
    poles=in_poles,
    ac_capacity=in_ac_capacity,
    substation_mva=in_substation_mva,
    state=in_state,
    title_no=in_title,
    lot_no=in_lot,
    owners_list=owners_list,
)
if validation_errors:
    for err in validation_errors:
        st.error(err)
    st.stop()

# --- Persist uploaded images to temp files for OCR ---
title_image_path = None
sld_image_path = None
if title_image_file:
    suffix = os.path.splitext(title_image_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(title_image_file.getvalue())
        title_image_path = tmp.name
if sld_image_file:
    suffix = os.path.splitext(sld_image_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(sld_image_file.getvalue())
        sld_image_path = tmp.name

# --- Build Grounded Land Metadata Object ---
try:
    land_meta, hectares, sq_meters, in_acres, in_roods, in_poles, owner_rows = build_land_metadata(
        title_no=in_title,
        lot_no=in_lot,
        state=in_state,
        zoning=in_zoning,
        acres=in_acres,
        roods=in_roods,
        poles=in_poles,
        caveats=in_caveats,
        charges=in_charges,
        reserve=in_reserve,
        owners_list=owners_list,
        title_image_path=title_image_path,
        project_company_name=in_project_company_name,
        project_company_reg_no=in_project_company_reg,
        source_type="SYNTHETIC_DEMO_OR_EDITED_FORM",
    )
except DocumentReviewRequired as exc:
    stop_with_review(str(exc), "Uploaded land title")
finally:
    if title_image_path and os.path.isfile(title_image_path):
        os.unlink(title_image_path)

legal_status = land_meta.legal_assessment.status
findings = land_meta.legal_assessment.findings
coowner_review_required = land_meta.legal_assessment.poa_compliance.requires_coowner_coordination
required_deeds = land_meta.legal_assessment.poa_compliance.required_deeds
total_share = sum(o.calculated_share_float for o in land_meta.owners)

# --- Run Base Technical Assessment ---
try:
    assessment = compute_assessment(
        land_meta=land_meta,
        slope_profile=in_slope_profile,
        ac_capacity=in_ac_capacity,
        substation_mva=in_substation_mva,
        site_mode=site_mode,
        sld_image_path=sld_image_path,
        scenario=in_scenario,
        voltage_class=in_voltage_class,
        maximum_demand_kw=in_maximum_demand if in_maximum_demand > 0 else None,
        hypothetical_bess=in_hypothetical_bess,
    )
except DocumentReviewRequired as exc:
    stop_with_review(str(exc), "Uploaded electrical SLD")
finally:
    if sld_image_path and os.path.isfile(sld_image_path):
        os.unlink(sld_image_path)
terrain_model = assessment["terrain_model"]
grid_audit = assessment["grid_audit"]
feasibility = assessment["feasibility"]
manifest = assessment["manifest"]
st.warning(f"PRELIMINARY SCREENING ONLY — Title source: {land_meta.source_type}; SLD source: {assessment['data_provenance']['sld']}; terrain: SYNTHETIC_TERRAIN. No legal or grid approval has been issued.")
if title_image_path or sld_image_path:
    st.caption(f"Google OCR model configured: {heliopolis_ocr.DEFAULT_MODEL}. Uploaded text remains unverified and needs human review. No data is sent without the permission checkbox.")
if in_scenario == "c_i_nem":
    st.info("Historical NEM NOVA sensitivity only. The published NEM 3.0 quota offer period ended June 2025; do not treat the modeled rate as a current application or Solar ATAP eligibility.")
if in_ac_capacity > 1.0:
    st.caption("Proposed capacity exceeds 1 MWac; do not present this project as eligible for non-domestic Solar ATAP.")

# --- Page Layout Tabs ---
tabs = st.tabs([
    "🔍 Site Prospector (Legal & Terrain)",
    "⚡ Electrical SLD Graph Audit",
    "📊 Financials & BESS Yield Sizing",
    "📄 SEDA & TNB Filing Manifests"
])

# ==========================================
# TAB 1: SITE PROSPECTOR
# ==========================================
with tabs[0]:
    c_status, c_hectares, c_sqm, c_land_type = st.columns(4)
    with c_status:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Preliminary Legal Flags</div>
            <div style="font-size: 1.5rem; font-weight: 800; margin-top: 0.5rem;">{status_badge(legal_status)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c_hectares:
        st.markdown(metric_card("Metric Area", f"{hectares:.4f} Ha", delta=f"{in_acres:.1f} Ekar", delta_type="up"), unsafe_allow_html=True)
    with c_sqm:
        st.markdown(metric_card("Square Meters", f"{sq_meters:,.1f} m²", delta="Imperial converted", delta_type="up"), unsafe_allow_html=True)
    with c_land_type:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Land Category & Lot</div>
            <div style="font-size: 1.25rem; font-weight: 800; margin-top: 0.5rem; color: var(--text);">{in_zoning} ({in_lot})</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    col_prosp_left, col_prosp_right = st.columns([7, 5])

    with col_prosp_left:
        st.markdown(clean_html_markdown(f"""
        <div class="card">
            <div class="card-title">Registered Landowners (Geran Tenancy Math)</div>
            <div class="card-subtitle">Co-ownership share evaluation under Malaysian National Land Code 1965</div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Landowner Name</th>
                        <th>MyKad IC / SSM Company No</th>
                        <th>Fraction Share</th>
                        <th>Decimal Share</th>
                    </tr>
                </thead>
                <tbody>
                    {owner_rows}
                    <tr style="background: var(--bg-subtle);">
                        <td><strong>Cumulative Total</strong></td>
                        <td>—</td>
                        <td><strong>120 / 120</strong></td>
                        <td><strong>{(total_share * 100.0):.1f}%</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """), unsafe_allow_html=True)

        # Power of Attorney & Joint-Execution Manifest Card
        poa_badge = '<span class="badge badge-amber">CO-OWNER REVIEW</span>' if coowner_review_required else '<span class="badge badge-amber">LEGAL REVIEW</span>'
        poa_reasons_html = "".join([f'<div class="checklist-item"><span class="checklist-dot"></span>{html_escape(d)}</div>' for d in required_deeds])

        st.markdown(clean_html_markdown(f"""
        <div class="card">
            <div class="card-title">Ownership / Instrument Review {poa_badge}</div>
            <div class="card-subtitle">Ownership shares are arithmetic facts, not sufficient evidence of legal execution authority</div>
            <div style="font-size: 0.8rem; margin-bottom: 0.8rem;">
                Confirm co-owner consent, legal capacity and title-specific instruments with a qualified solicitor or land office.
            </div>
            {poa_reasons_html}
        </div>
        """), unsafe_allow_html=True)

    with col_prosp_right:
        # Legal Findings Checklist
        findings_html = ""
        if findings:
            for f in findings:
                findings_html += f'<div class="checklist-item"><span class="checklist-dot" style="background: var(--red);"></span>{html_escape(f)}</div>'
        else:
            findings_html = '<div class="checklist-item"><span class="checklist-dot" style="background: var(--green);"></span>No selected restriction flags were reported. Legal status remains unverified.</div>'

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Legal Encumbrances & Restrictions Checklist</div>
            <div class="card-subtitle">Preliminary screening from reported title fields; not a land-office search</div>
            {findings_html}
        </div>
        """, unsafe_allow_html=True)

        # Terrain Profile
        terrain_risk_badge = "badge-green" if "Optimal" in in_slope_profile else ("badge-amber" if "Rolling" in in_slope_profile else "badge-red")
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Topographic Slope Profile <span class="badge {terrain_risk_badge}">{terrain_model.landslide_risk.upper()}</span></div>
            <div class="card-subtitle">2D Spatial Finite-Difference Terrain Modeling</div>
            <table class="data-table">
                <tbody>
                    <tr>
                        <td>Mean Slope (Degrees)</td>
                        <td><strong>{terrain_model.mean_slope_degrees}°</strong></td>
                    </tr>
                    <tr>
                        <td>Optimal Zone (&lt; 5°) Area</td>
                        <td><strong>{terrain_model.optimal_area_percent}%</strong></td>
                    </tr>
                    <tr>
                        <td>Manageable Zone (5° - 15°) Area</td>
                        <td><strong>{terrain_model.manageable_area_percent}%</strong></td>
                    </tr>
                    <tr>
                        <td>Critical Zone (&gt; 15°) Area</td>
                        <td><strong style="color: var(--red);">{terrain_model.critical_area_percent}%</strong></td>
                    </tr>
                    <tr>
                        <td>Civil Grading CAPEX Multiplier</td>
                        <td><strong>{terrain_model.grading_capex_premium_multiplier:.2f}x</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 2: ELECTRICAL SLD GRAPH AUDIT
# ==========================================
with tabs[1]:
    # Let's create an interactive single-line diagram graph representation
    st.markdown('<div class="brand-name" style="margin-bottom: 0.5rem;">Single-Line Diagram (SLD) Topology Audit</div>', unsafe_allow_html=True)

    col_sld_ctrl, col_sld_chart = st.columns([5, 7])

    with col_sld_ctrl:
        st.markdown('<div class="card-title">Preliminary Drawing Connectivity Review</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.8rem; margin-bottom: 1rem;">Assess a limited set of drawing connectivity relationships. This cannot certify protection or grid-code compliance.</div>', unsafe_allow_html=True)

        if sld_image_path:
            st.caption(
                "Uploaded drawing: selected voltage class is a USER ASSUMPTION, "
                "not inferred TNB connection approval. Demo controls are disabled."
            )
        else:
            st.caption(
                f"SYNTHETIC {in_voltage_class} fixture. Select LV/MV in the "
                "sidebar to choose the modeled drawing layout."
            )
        if in_voltage_class == "LV":
            has_relay = st.toggle(
                "Explicit inverter anti-islanding label shown (synthetic)",
                value=True, disabled=bool(sld_image_path),
            )
            is_xfmr_connected = st.toggle(
                "Connect inverter to grid (synthetic)",
                value=True, disabled=bool(sld_image_path),
            )
        else:
            has_relay = st.toggle(
                "Include separate Anti-Islanding Relay (synthetic)",
                value=True, disabled=bool(sld_image_path),
            )
            is_xfmr_connected = st.toggle(
                "Connect Transformer to Grid (synthetic)",
                value=True, disabled=bool(sld_image_path),
            )

        # Never rerun an uploaded OCR/model or financial assessment for this tab.
        # The cheap fixture toggle only changes the displayed synthetic graph.
        g = (
            assessment["sld_graph"]
            if sld_image_path
            else build_demo_sld(
                has_relay=has_relay,
                is_xfmr_connected=is_xfmr_connected,
                connection_profile=in_voltage_class,
            )
        )

        topology = g.graph.get("tnb_compliance", {})
        st.markdown("---")
        st.markdown('<div class="card-title">Preliminary SLD Topology Screen</div>', unsafe_allow_html=True)
        st.caption(
            f"Connection profile: {html_escape(str(topology.get('connection_profile', 'UNKNOWN')))} "
            "(user assumed). Checks only drawing connectivity / explicit labels; "
            "not inverter anti-islanding certification or TNB approval."
        )
        if topology.get("preliminary_topology_status") == "PRELIMINARY_TOPOLOGY_PASS":
            if topology.get("connection_profile") == "LV":
                st.success(
                    "LV preliminary topology: modeled PV → inverter → grid path with "
                    "an explicit anti-islanding label (or connected external protection). "
                    "Inverter certification, AC switches, metering, settings and TNB "
                    "approval remain UNVERIFIED."
                )
            else:
                st.success(
                    "MV preliminary topology: connected modeled PV → inverter → relay "
                    "→ transformer → grid path. Independent engineering review remains required."
                )
        else:
            st.error("NEEDS REVIEW: " + "; ".join(topology.get("findings", ["Incomplete or ambiguous SLD topology."])))

    with col_sld_chart:
        # Recreate horizontal networkx plot
        node_colors = []
        node_sizes = []
        labels = {}
        for node, data in g.nodes(data=True):
            style = _sld_node_style(data.get("category", ""), node)
            node_colors.append(style["color"])
            node_sizes.append(style["size"])
            labels[node] = style["label"]

        fig, ax = plt.subplots(figsize=(10, 5), facecolor="none")
        ax.set_facecolor("none")

        pos = {node: (i + 1, 1) for i, node in enumerate(g.nodes())}

        nx.draw_networkx_nodes(g, pos, ax=ax, node_color=node_colors, node_size=node_sizes, alpha=0.9, edgecolors="white" if IS_DARK else "black")
        nx.draw_networkx_edges(g, pos, ax=ax, width=2, arrowsize=20, edge_color="white" if IS_DARK else "black", min_source_margin=15, min_target_margin=15)
        nx.draw_networkx_labels(g, pos, labels=labels, ax=ax, font_size=8, font_family="sans-serif", font_weight="bold", font_color="white" if IS_DARK else "black")

        plt.axis("off")
        st.pyplot(fig, clear_figure=True)

# ==========================================
# TAB 3: FINANCIALS & BESS YIELD SIZING
# ==========================================
with tabs[2]:
    st.markdown('<div class="brand-name" style="margin-bottom: 0.5rem;">Tropical Yield Sizing & Financial Model (Newton-Raphson)</div>', unsafe_allow_html=True)

    col_fin_1, col_fin_2, col_fin_3, col_fin_4 = st.columns(4)
    with col_fin_1:
        st.markdown(metric_card("Simulated DC Peak", f"{feasibility.capacity_mwp:.3f} MWp", delta="Mono-PERC Mono Grid", delta_type="up"), unsafe_allow_html=True)
    with col_fin_2:
        st.markdown(metric_card("Annual Yield", f"{feasibility.annual_yield_mwh:,.1f} MWh/year", delta="Tropical temp derated", delta_type="up"), unsafe_allow_html=True)
    with col_fin_3:
        capex_delta_type = "down" if feasibility.grading_adjusted_capex_rm > feasibility.base_capex_rm else "up"
        st.markdown(metric_card("Final CAPEX Cost", f"RM {feasibility.grading_adjusted_capex_rm:,.2f}", delta=f"{((feasibility.grading_adjusted_capex_rm - feasibility.base_capex_rm) / 1000000.0):.2f}M Premiums added", delta_type=capex_delta_type), unsafe_allow_html=True)
    with col_fin_4:
        if feasibility.irr_percent is None:
            st.markdown(metric_card("Project IRR", "Not estimated",
                delta="Customer load/tariff evidence missing", delta_type="warning"),
                unsafe_allow_html=True)
        else:
            irr_delta_type = "up" if feasibility.irr_percent > 6.5 else "down"
            st.markdown(metric_card("Illustrative IRR", f"{feasibility.irr_percent:.2f}%",
                delta="No signed PPA or bankable yield", delta_type=irr_delta_type),
                unsafe_allow_html=True)

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    col_fin_left, col_fin_right = st.columns([7, 5])

    with col_fin_left:
        if feasibility.financial_status != "ILLUSTRATIVE_LSS_PPA_NO_SIGNED_CONTRACT":
            st.info("NPV, IRR and net cash-flow chart withheld: customer interval demand/export, applicable tariff, and 10-year offset limits are not verified. Gross yield and LCOE above are illustrative only.")
        else:
            # Build Cash Flow Plot using Plotly Go
            st.markdown('<div class="card-title">Illustrative LSS PPA Cash Flows (21 years)</div>', unsafe_allow_html=True)

            # Use the same lifecycle projection function as the backend engine.
            projection = project_lifecycle_cashflows(
                capacity_mwp=feasibility.capacity_mwp,
                annual_yield_mwh=feasibility.annual_yield_mwh,
                adjusted_capex_rm=feasibility.grading_adjusted_capex_rm,
                bess_capex_rm=grid_audit.bess_specification.estimated_bess_capex_rm,
                tariff_rm_kwh=feasibility.ppa_tariff_rm_kwh,
            )
            years = list(range(0, len(projection["cash_flows"])))
            cf_vals = projection["cash_flows"]

            fig_cf = go.Figure()
            fig_cf.add_trace(go.Bar(
                x=years,
                y=cf_vals,
                marker_color=["#ef4444" if val < 0 else "#22c55e" for val in cf_vals],
                name="Net Cash Flow"
            ))

            fig_cf.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", color="#71717a" if not IS_DARK else "#a1a1aa", size=10),
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(
                    gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
                    tickmode="linear",
                    dtick=2,
                    title="Year"
                ),
                yaxis=dict(
                    gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
                    title="Net Cash Flow (RM)"
                ),
                height=300
            )
            st.plotly_chart(fig_cf, use_container_width=True, config={"displayModeBar": False})

    with col_fin_right:
        # BESS Battery Specification Card
        bess = grid_audit.bess_specification
        bess_badge = '<span class="badge badge-amber">UTILITY STUDY NEEDED</span>'

        bess_reasons_html = "".join(
            f'<div class="checklist-item"><span class="checklist-dot" style="background: var(--amber);"></span>{reason}</div>'
            for reason in bess.reasons
        )

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Preliminary Grid Ratio / Optional BESS Sensitivity {bess_badge}</div>
            <div class="card-subtitle">Illustrative MW/MVA ratio; no load-flow model or automatic BESS requirement</div>
            <table class="data-table">
                <tbody>
                    <tr>
                        <td>Upstream Substation Limit</td>
                        <td><strong>{grid_audit.upstream_substation_capacity_mva:.1f} MVA</strong></td>
                    </tr>
                    <tr>
                        <td>Solar Peak Injection Ratio</td>
                        <td><strong>{grid_audit.substation_injection_percent}%</strong></td>
                    </tr>
                    <tr>
                        <td>Hypothetical BESS Power (off by default)</td>
                        <td><strong>{bess.recommended_battery_power_mw:.2f} MW</strong></td>
                    </tr>
                    <tr>
                        <td>Hypothetical BESS Capacity</td>
                        <td><strong>{bess.recommended_battery_capacity_mwh:.2f} MWh (4-hr)</strong></td>
                    </tr>
                    <tr>
                        <td>Hypothetical BESS CAPEX</td>
                        <td><strong>RM {bess.estimated_bess_capex_rm:,.2f}</strong></td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top: 1rem;">
                {bess_reasons_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 4: SEDA & TNB FILING MANIFESTS
# ==========================================
with tabs[3]:
    st.markdown('<div class="brand-name" style="margin-bottom: 0.5rem;">Preliminary SEDA / TNB Planning Fields (Not a Filed Application)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.8rem; margin-bottom: 1.25rem;">These are indicative planning fields only; actual filing, eligibility and grid requirements require qualified review.</div>', unsafe_allow_html=True)

    # Canonical planning fields come from land_meta; do not override an
    # OCR-extracted title/location with stale sidebar or hard-coded Perak values.
    seda = manifest.seda_application
    tnb = manifest.tnb_grid_request
    atap_screen = manifest.solar_atap_precheck
    study = manifest.nemas_checklist

    col_man_left, col_man_right = st.columns(2)

    with col_man_left:
        # SEDA Form Part A & B
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Preliminary Scheme Planning Data (Not a SEDA Application)</div>
            <div class="card-subtitle">Source-preserving input summary, not an official form</div>
            <table class="data-table">
                <tbody>
                    <tr>
                        <td style="width: 40%;">Part A: Applicant Corporate Name</td>
                        <td><strong>{html_escape(seda.Part_A_Applicant_Name)}</strong></td>
                    </tr>
                    <tr>
                        <td>Part A: SSM Company No</td>
                        <td><code>{html_escape(seda.Part_A_Company_Registration)}</code></td>
                    </tr>
                    <tr>
                        <td>Part B: Registered Title Reference</td>
                        <td><strong>{html_escape(seda.Part_B_Site_Title_Number)} ({html_escape(seda.Part_B_Site_Lot_Number)})</strong></td>
                    </tr>
                    <tr>
                        <td>Part B: Site Mukim & State</td>
                        <td><strong>{html_escape(seda.Part_B_Mukim_Daerah_Negeri)}</strong></td>
                    </tr>
                    <tr>
                        <td>Part C: Proposed DC Capacity</td>
                        <td><strong>{seda.Part_C_Proposed_DC_Capacity_kWp:,.2f} kWp</strong></td>
                    </tr>
                    <tr>
                        <td>Part C: Proposed AC Capacity</td>
                        <td><strong>{seda.Part_C_Proposed_AC_Capacity_kWac:,.2f} kWac</strong></td>
                    </tr>
                    <tr>
                        <td>Illustrative Model Tariff / Offset Assumption</td>
                        <td><strong>RM {seda.Part_D_PPA_Tariff_Rate_RM_kWh:.4f} / kWh (not a signed tariff or LCOE)</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # TNB Grid Connection Specs
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Connection Assumptions (Not a TNB Design)</div>
            <div class="card-subtitle">Connection class is selected by user; exact voltage and PCC are unverified</div>
            <table class="data-table">
                <tbody>
                    <tr>
                        <td style="width: 40%;">Interconnection Voltage Level</td>
                        <td><strong>Not engineered; selected class: {html_escape(study.voltage_class)}</strong></td>
                    </tr>
                    <tr>
                        <td>Total Generation Capacity</td>
                        <td><strong>{(seda.Part_C_Proposed_AC_Capacity_kWac / 1000.0):.2f} MWac</strong></td>
                    </tr>
                    <tr>
                        <td>Standards to verify (not certified)</td>
                        <td><strong>{", ".join(tnb.Inverter_Compliance_Standards)}</strong></td>
                    </tr>
                    <tr>
                        <td>Point of Common Coupling (PCC)</td>
                        <td><strong>{html_escape(tnb.Point_of_Common_Coupling)}</strong></td>
                    </tr>
                    <tr>
                        <td>Transformer Capacity</td>
                        <td><strong>To be determined by qualified engineering design</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_man_right:
        # Study fees are for the modeled financial scheme and applicable
        # voltage band; do not override with a universal >72 kW rule.
        nemas = manifest.nemas_checklist
        study_label = nemas.assessment_type.replace("_", " ")
        nemas_fee_text = (
            f"RM {nemas.estimated_regulatory_fee_rm:,.2f} (historical NOVA reference only)"
            if nemas.estimated_regulatory_fee_rm is not None
            else "Unknown / not applicable / requires specific study"
        )
        study_notes = "".join(
            f'<div class="checklist-item"><span class="checklist-dot" style="background: var(--amber);"></span>{note}</div>'
            for note in nemas.eligibility_notes + nemas.mandatory_technical_studies
        )
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Preliminary Connection Study Screen</div>
            <div class="card-subtitle">No filing, technical study or approval has been completed.</div>
            <table class="data-table">
                <tbody>
                    <tr><td>Proposed AC Capacity</td><td>{in_ac_capacity * 1000:,.1f} kWac</td></tr>
                    <tr><td>Study Classification</td><td>{study_label}</td></tr>
                    <tr><td>Connection Voltage Class</td><td>{nemas.voltage_class} (assumed)</td></tr>
                    <tr><td>Published Historical Fee Reference</td><td>{nemas_fee_text}</td></tr>
                    <tr><td>Processing Time</td><td>Not verified</td></tr>
                </tbody>
            </table>
            {study_notes}
        </div>
        """, unsafe_allow_html=True)
        if nemas.source_url:
            st.caption(f"Study reference: {nemas.source_url} — {nemas.source_version}. Historical data do not establish a current application right.")
        if atap_screen:
            st.markdown("#### Solar ATAP: capacity-only precheck (NOT a financial simulation)")
            if atap_screen.status == "CAPACITY_SCREEN_ONLY_FURTHER_REVIEW_REQUIRED":
                st.info("Capacity is within the stated cap/maximum-demand limits, but eligibility and electrical assessment remain unverified.")
            else:
                st.warning(f"ATAP precheck: {atap_screen.status.replace('_', ' ').lower()}.")
            st.caption("Export offsets only within the initial 10-year programme term; customer load and credits are NOT modeled.")

        # Download button
        report_payload = {
            "scope": "PRELIMINARY_SCREENING_ONLY; NO LEGAL/TNB/SEDA APPROVAL",
            "assessment_status": "PRELIMINARY_REVIEW_REQUIRED",
            "data_provenance": {**assessment["data_provenance"], "sld": g.graph.get("source_type", "SYNTHETIC_DEMO")},
            "sld_topology_screen": g.graph.get("tnb_compliance", {}),
            "regulatory_study": manifest.nemas_checklist.model_dump(),
            "regulatory_planning_fields": {
                "seda": manifest.seda_application.model_dump(),
                "tnb": manifest.tnb_grid_request.model_dump(),
            },
            "solar_atap_capacity_only_precheck": (
                manifest.solar_atap_precheck.model_dump() if manifest.solar_atap_precheck else None
            ),
            "ocr_status": {
                "title": "OCR_EXTRACTED_UNVERIFIED" if land_meta.source_type == "OCR_EXTRACTED_UNVERIFIED" else "NOT_USED",
                "sld": "OCR_EXTRACTED_UNVERIFIED" if g.graph.get("source_type") == "OCR_EXTRACTED_UNVERIFIED" else "NOT_USED",
                "model": heliopolis_ocr.DEFAULT_MODEL if (title_image_path or sld_image_path) else None,
                "third_party_cloud_upload_authorized": bool(allow_cloud_ocr) if (title_image_path or sld_image_path) else False,
            },
            "land_title_analysis": {
                "title_no": land_meta.title_no, "lot_no": land_meta.lot_no, "state": land_meta.state,
                "area_hectares": hectares, "area_sq_meters": sq_meters,
                "has_caveats": land_meta.has_caveats, "has_charges": land_meta.has_charges, "is_malay_reserve": land_meta.is_malay_reserve,
                "legal_status": legal_status, "source_type": land_meta.source_type, "review_status": land_meta.review_status
            },
            "terrain_profile": {
                "mean_slope_degrees": terrain_model.mean_slope_degrees,
                "landslide_risk": terrain_model.landslide_risk,
                "grading_multiplier": terrain_model.grading_capex_premium_multiplier
            },
            "financial_feasibility": {
                "scenario": feasibility.scenario,
                "assumption_status": "ILLUSTRATIVE_NOT_BANKABLE",
                "capacity_mwp": feasibility.capacity_mwp,
                "annual_yield_mwh": feasibility.annual_yield_mwh,
                "adjusted_capex_rm": feasibility.grading_adjusted_capex_rm,
                "project_npv_rm": feasibility.npv_rm,
                "project_irr_percent": feasibility.irr_percent,
                "financial_status": feasibility.financial_status,
                "financial_notes": feasibility.financial_notes
            }
        }
        json_str = json.dumps(report_payload, indent=4)
        st.download_button(
            label="💾 Download Structured Solar Assessment Report (JSON)",
            data=json_str,
            file_name="solar_assessment_report.json",
            mime="application/json",
            use_container_width=True
        )

