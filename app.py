import os
import sys
import json
import tempfile
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
from app_logic import (
    get_state_from_region,
    generate_co_owners,
    build_land_metadata,
    compute_assessment,
    dnn_inference,
    _sld_node_style,
)

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
        Neural-Symbolic Site Prospection & Regulatory Compliance Auditor (Peninsular Malaysia NLC 1965 & TNB Grid Standards)
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
    site_mode = st.radio("Selection Mode", ["Standard Presets", "Real Malaysian Sites (500)"], horizontal=True, key="site_mode_selector")

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

            # Pre-populate tab 5 features for the selected preset
            if selected_preset == "Perak Site (Default High Slope)":
                st.session_state.in_max_slope = 37.7 * 1.8
                st.session_state.in_grid_dist = 2.5
                st.session_state.in_owners_count = 5
            elif selected_preset == "Kedah Plain (Flat - Optimal)":
                st.session_state.in_max_slope = 2.1 * 1.8
                st.session_state.in_grid_dist = 1.2
                st.session_state.in_owners_count = 3
            else:
                st.session_state.in_max_slope = 8.5 * 1.8
                st.session_state.in_grid_dist = 3.8
                st.session_state.in_owners_count = 4

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
        selected_site_str = st.selectbox("Select Real Malaysian Site", site_options, key="site_selector")

        if selected_site_str:
            selected_idx = site_options.index(selected_site_str)
            site_data = filtered_sites[selected_idx]

            # If selection mode or target changed, update inputs in session_state
            if st.session_state.prev_selected_mode != "Real Malaysian Sites" or st.session_state.prev_selected_site != site_data["site_id"]:
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

                # Pre-populate tab 5 features for the selected real site
                st.session_state.in_max_slope = float(site_data["max_slope_degrees"])
                st.session_state.in_grid_dist = float(site_data["grid_proximity_km"])
                st.session_state.in_owners_count = int(site_data["co_owners_count"])

                st.session_state.prev_selected_mode = "Real Malaysian Sites"
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

    st.markdown('<div class="card-title">Technical Specifications</div>', unsafe_allow_html=True)
    current_slope_profile = st.session_state.get("in_slope_profile", "Severe Ridge (37.7° mean)")
    slope_profiles_list = SLOPE_PROFILES.copy()
    if current_slope_profile not in slope_profiles_list:
        slope_profiles_list.append(current_slope_profile)
    in_slope_profile = st.selectbox("Terrain Slope Profile", slope_profiles_list, index=slope_profiles_list.index(current_slope_profile))

    in_ac_capacity = st.number_input("Proposed AC Capacity (MWac)", value=st.session_state.get("in_ac_capacity", 3.21), step=0.1)
    in_substation_mva = st.number_input("Upstream Substation Limit (MVA)", value=st.session_state.get("in_substation_mva", 15.0), step=1.0)

    st.markdown("---")
    st.markdown('<div class="card-title">Scanned Document OCR</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.5rem;">Upload images to run real Gemini OCR. Leave blank to use the form values above.</div>', unsafe_allow_html=True)
    title_image_file = st.file_uploader("Land Title Scan (PNG/JPG)", type=["png", "jpg", "jpeg"])
    sld_image_file = st.file_uploader("SLD Diagram Scan (PNG/JPG)", type=["png", "jpg", "jpeg"])

# --- Compute Ownership Splits ---
if site_mode == "Real Malaysian Sites (500)":
    active_site_id = st.session_state.get("prev_selected_site", "MY-SITE-0001")
    matching_site = next((s for s in real_sites if s["site_id"] == active_site_id), None)
    co_owners_cnt = matching_site["co_owners_count"] if matching_site else 5
    owners_list = generate_co_owners(co_owners_cnt, active_site_id)
else:
    owners_list = SAMPLE_OWNERS

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
)

legal_status = land_meta.legal_assessment.status
findings = land_meta.legal_assessment.findings
is_poa_required = land_meta.legal_assessment.poa_compliance.is_poa_required
required_deeds = land_meta.legal_assessment.poa_compliance.required_deeds
total_share = sum(o.calculated_share_float for o in land_meta.owners)

# --- Run Base Technical Assessment ---
assessment = compute_assessment(
    land_meta=land_meta,
    slope_profile=in_slope_profile,
    ac_capacity=in_ac_capacity,
    substation_mva=in_substation_mva,
    site_mode=site_mode,
    sld_image_path=sld_image_path,
)
terrain_model = assessment["terrain_model"]
grid_audit = assessment["grid_audit"]
feasibility = assessment["feasibility"]
manifest = assessment["manifest"]

# --- Page Layout Tabs ---
tabs = st.tabs([
    "🔍 Site Prospector (Legal & Terrain)",
    "⚡ Electrical SLD Graph Audit",
    "📊 Financials & BESS Yield Sizing",
    "📄 SEDA & TNB Filing Manifests",
    "🧠 HeliopolisDNN SwiGLU Inference"
])

# ==========================================
# TAB 1: SITE PROSPECTOR
# ==========================================
with tabs[0]:
    c_status, c_hectares, c_sqm, c_land_type = st.columns(4)
    with c_status:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Legal Land Status</div>
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
        poa_badge = '<span class="badge badge-amber">POA REQUIRED</span>' if is_poa_required else '<span class="badge badge-green">POA NOT REQUIRED</span>'
        poa_reasons_html = "".join([f'<div class="checklist-item"><span class="checklist-dot"></span>{d}</div>' for d in required_deeds]) if is_poa_required else '<div class="checklist-item"><span class="checklist-dot"></span>Single controlling entity holds ≥50% share; standard lease can be registered directly without Power of Attorney.</div>'

        st.markdown(clean_html_markdown(f"""
        <div class="card">
            <div class="card-title">Joint-Execution Power of Attorney Manifest {poa_badge}</div>
            <div class="card-subtitle">Minimum co-owners signature count required to bypass 51% controlling interest threshold</div>
            <div style="font-size: 0.8rem; margin-bottom: 0.8rem;">
                To legally lease or acquire this land for solar utility deployment under NLC Section 124, a controlling interest must be established.
            </div>
            {poa_reasons_html}
        </div>
        """), unsafe_allow_html=True)

    with col_prosp_right:
        # Legal Findings Checklist
        findings_html = ""
        if findings:
            for f in findings:
                findings_html += f'<div class="checklist-item"><span class="checklist-dot" style="background: var(--red);"></span>{f}</div>'
        else:
            findings_html = '<div class="checklist-item"><span class="checklist-dot" style="background: var(--green);"></span>No critical legal encumbrances, caveats, charges, or reserve flags detected. Clear title.</div>'

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Legal Encumbrances & Restrictions Checklist</div>
            <div class="card-subtitle">NLP Named Entity Recognition audit against administrative land titles</div>
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
        st.markdown('<div class="card-title">TNB ESAG Grid Code Auditor</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.8rem; margin-bottom: 1rem;">Verify if the electrical schematic contains necessary protective coordinates before submitting to Tenaga Nasional Berhad (TNB).</div>', unsafe_allow_html=True)

        has_relay = st.toggle("Include Anti-Islanding Protection Relay", value=True)
        is_xfmr_connected = st.toggle("Connect Transformer safely to Grid Incomer", value=True)

        # Recompute SLD graph based on user switches or uploaded OCR image
        sld_assessment = compute_assessment(
            land_meta=land_meta,
            slope_profile=in_slope_profile,
            ac_capacity=in_ac_capacity,
            substation_mva=in_substation_mva,
            site_mode=site_mode,
            has_relay=has_relay,
            is_xfmr_connected=is_xfmr_connected,
            sld_image_path=sld_image_path,
        )
        g = sld_assessment["sld_graph"]

        relay_present = "RELAY_1" in g.nodes()
        path_exists = nx.has_path(g, "XFMR_1", "GRID_1") if ("XFMR_1" in g.nodes() and "GRID_1" in g.nodes()) else False

        st.markdown("---")
        st.markdown('<div class="card-title">Live Grid Code Verification Result</div>', unsafe_allow_html=True)

        if relay_present:
            st.markdown('<div class="checklist-item"><span class="checklist-dot" style="background: var(--green);"></span><strong>PASS:</strong> Anti-Islanding Protection Relay correctly integrated into circuit.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="checklist-item"><span class="checklist-dot" style="background: var(--red);"></span><strong>VIOLATION:</strong> TNB Code ESAG Section 3.2.1: Anti-Islanding Protection Relay missing from schematic. Connection will be rejected.</div>', unsafe_allow_html=True)

        if path_exists:
            st.markdown('<div class="checklist-item"><span class="checklist-dot" style="background: var(--green);"></span><strong>PASS:</strong> Safe path verified from local generation transformer to grid incomer point.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="checklist-item"><span class="checklist-dot" style="background: var(--red);"></span><strong>VIOLATION:</strong> Floating Circuitry: No continuous conductive electrical path detected from Transformer to TNB Grid Incomer.</div>', unsafe_allow_html=True)

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
        irr_delta_type = "up" if feasibility.irr_percent > 6.5 else "down"
        st.markdown(metric_card("Project IRR (%)", f"{feasibility.irr_percent:.2f}%", delta="Newton-Raphson Solver", delta_type=irr_delta_type), unsafe_allow_html=True)

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    col_fin_left, col_fin_right = st.columns([7, 5])

    with col_fin_left:
        # Build Cash Flow Plot using Plotly Go
        st.markdown('<div class="card-title">21-Year Lifecycle Projected Net Cash Flows</div>', unsafe_allow_html=True)

        years = list(range(0, 22))
        cf_vals = [-feasibility.grading_adjusted_capex_rm]

        # Recalculate cash flows for plotting
        bess_addition_capex = grid_audit.bess_specification.estimated_bess_capex_rm
        bess_opex = bess_addition_capex * 0.015 if bess_addition_capex > 0 else 0.0
        for yr in range(1, 22):
            degradation = (1.0 - 0.005) ** (yr - 1)
            gen = feasibility.annual_yield_mwh * 1000.0 * degradation
            opex = (feasibility.capacity_mwp * 45000.0 + bess_opex) * (1.02) ** (yr - 1)
            rev = gen * 0.23  # average NEM NOVA tariff RM 0.23
            cf_vals.append(rev - opex)

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
        bess_badge = '<span class="badge badge-red">BESS REQUIRED</span>' if bess.is_bess_required else '<span class="badge badge-green">GRID COMPLIANT</span>'

        bess_reasons_html = ""
        if bess.is_bess_required:
            for r in bess.reasons:
                bess_reasons_html += f'<div class="checklist-item"><span class="checklist-dot" style="background: var(--red);"></span>{r}</div>'
        else:
            bess_reasons_html = '<div class="checklist-item"><span class="checklist-dot" style="background: var(--green);"></span>Proposed solar AC capacity sits comfortably below the Upstream TNB Substation 15% thermal load-flow threshold. No battery storage required for grid injection.</div>'

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Battery Energy Storage Sizing (BESS) {bess_badge}</div>
            <div class="card-subtitle">Peak-Shaving Lithium Iron Phosphate (LFP) Sizing Module</div>
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
                        <td>Recommended BESS Power</td>
                        <td><strong>{bess.recommended_battery_power_mw:.2f} MW</strong></td>
                    </tr>
                    <tr>
                        <td>Recommended BESS Capacity</td>
                        <td><strong>{bess.recommended_battery_capacity_mwh:.2f} MWh (4-hr)</strong></td>
                    </tr>
                    <tr>
                        <td>Estimated BESS CAPEX</td>
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
    st.markdown('<div class="brand-name" style="margin-bottom: 0.5rem;">Pre-filled SEDA & TNB Regulatory Application Manifests</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.8rem; margin-bottom: 1.25rem;">Heliopolis-AI automatically maps civil, legal, and financial dimensions to structure pre-filled filings for Malaysian grid-connection requests.</div>', unsafe_allow_html=True)

    # Patch values from sidebar
    seda = manifest.seda_application
    tnb = manifest.tnb_grid_request
    seda.Part_B_Site_Title_Number = in_title
    seda.Part_B_Site_Lot_Number = in_lot
    seda.Part_B_Mukim_Daerah_Negeri = f"Mukim Asam Kumbang, Larut dan Matang, {in_state}"
    seda.Part_C_Proposed_DC_Capacity_kWp = float(feasibility.capacity_mwp * 1000.0)
    seda.Part_C_Proposed_AC_Capacity_kWac = float(in_ac_capacity * 1000.0)
    seda.Part_D_PPA_Tariff_Rate_RM_kWh = float(feasibility.lcoe_rm_kwh)

    col_man_left, col_man_right = st.columns(2)

    with col_man_left:
        # SEDA Form Part A & B
        st.markdown(f"""
        <div class="card">
            <div class="card-title">SEDA Rakyat Net Energy Metering (NEM / NOVA) Request</div>
            <div class="card-subtitle">Form Pre-Fill Part A, B, C & D</div>
            <table class="data-table">
                <tbody>
                    <tr>
                        <td style="width: 40%;">Part A: Applicant Corporate Name</td>
                        <td><strong>{seda.Part_A_Applicant_Name}</strong></td>
                    </tr>
                    <tr>
                        <td>Part A: SSM Company No</td>
                        <td><code>{seda.Part_A_Company_Registration}</code></td>
                    </tr>
                    <tr>
                        <td>Part B: Registered Title Reference</td>
                        <td><strong>{seda.Part_B_Site_Title_Number} ({seda.Part_B_Site_Lot_Number})</strong></td>
                    </tr>
                    <tr>
                        <td>Part B: Site Mukim & State</td>
                        <td><strong>{seda.Part_B_Mukim_Daerah_Negeri}</strong></td>
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
                        <td>Part D: Proposed PPA Tariff Rate</td>
                        <td><strong>RM {seda.Part_D_PPA_Tariff_Rate_RM_kWh:.4f} / kWh (LCOE-based)</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # TNB Grid Connection Specs
        st.markdown(f"""
        <div class="card">
            <div class="card-title">TNB Medium-Voltage Grid Connection Specs</div>
            <div class="card-subtitle">Grid Parallel Interconnection Filing Requirements</div>
            <table class="data-table">
                <tbody>
                    <tr>
                        <td style="width: 40%;">Interconnection Voltage Level</td>
                        <td><strong>{tnb.Interconnection_Voltage_Level_kV:.1f} kV (Medium Voltage)</strong></td>
                    </tr>
                    <tr>
                        <td>Total Generation Capacity</td>
                        <td><strong>{(seda.Part_C_Proposed_AC_Capacity_kWac / 1000.0):.2f} MWac</strong></td>
                    </tr>
                    <tr>
                        <td>Inverter Compliance Standards</td>
                        <td><strong>{", ".join(tnb.Inverter_Compliance_Standards)}</strong></td>
                    </tr>
                    <tr>
                        <td>Point of Common Coupling (PCC)</td>
                        <td><strong>{tnb.Point_of_Common_Coupling}</strong></td>
                    </tr>
                    <tr>
                        <td>Sized Transformer Capacity</td>
                        <td><strong>{(seda.Part_C_Proposed_AC_Capacity_kWac / 1000.0 * 1.25):.2f} MVA</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_man_right:
        # NEMAS Checklist Card
        nemas = manifest.nemas_checklist
        # Override based on sidebar input capacity
        nemas.is_nemas_required = (in_ac_capacity * 1000.0) > 72.0

        nemas_badge = '<span class="badge badge-red">NEMAS MANDATORY</span>' if nemas.is_nemas_required else '<span class="badge badge-green">NEMAS EXEMPT</span>'
        nemas_fee_val = 8000.0 if nemas.is_nemas_required else 0.0
        nemas_days_val = 90 if nemas.is_nemas_required else 15

        nemas_studies_html = ""
        if nemas.is_nemas_required:
            for s in nemas.mandatory_technical_studies:
                nemas_studies_html += f'<div class="checklist-item"><span class="checklist-dot" style="background: var(--amber);"></span>{s}</div>'
        else:
            nemas_studies_html = '<div class="checklist-item"><span class="checklist-dot" style="background: var(--green);"></span>Exempt: proposed AC capacity sits comfortably below the 72 kWac net metering assessment study threshold. Direct fast-track connection approved.</div>'

        st.markdown(f"""
        <div class="card">
            <div class="card-title">SEDA NEMAS Grid Assessment Study Checklist {nemas_badge}</div>
            <div class="card-subtitle">Required Studies for AC Capacity Exceeding 72 kWac</div>
            <table class="data-table">
                <tbody>
                    <tr>
                        <td style="width: 50%;">NEMAS Study Trigger Threshold</td>
                        <td><strong>&gt; 72.0 kWac</strong></td>
                    </tr>
                    <tr>
                        <td>Proposed Plant AC Capacity</td>
                        <td><strong>{(in_ac_capacity * 1000.0):,.1f} kWac</strong></td>
                    </tr>
                    <tr>
                        <td>Estimated Regulatory Review Fees</td>
                        <td><strong>RM {nemas_fee_val:,.2f}</strong></td>
                    </tr>
                    <tr>
                        <td>Estimated Processing Duration</td>
                        <td><strong>{nemas_days_val} Calendar Days</strong></td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top: 1rem; font-weight: 600; font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Mandatory Engineering Studies:</div>
            {nemas_studies_html}
        </div>
        """, unsafe_allow_html=True)

        # Download button
        report_payload = {
            "land_title_analysis": {
                "title_no": in_title, "lot_no": in_lot, "state": in_state,
                "area_hectares": hectares, "area_sq_meters": sq_meters,
                "has_caveats": in_caveats, "has_charges": in_charges, "is_malay_reserve": in_reserve,
                "legal_status": legal_status
            },
            "terrain_profile": {
                "mean_slope_degrees": terrain_model.mean_slope_degrees,
                "landslide_risk": terrain_model.landslide_risk,
                "grading_multiplier": terrain_model.grading_capex_premium_multiplier
            },
            "financial_feasibility": {
                "capacity_mwp": feasibility.capacity_mwp,
                "annual_yield_mwh": feasibility.annual_yield_mwh,
                "adjusted_capex_rm": feasibility.grading_adjusted_capex_rm,
                "project_npv_rm": feasibility.npv_rm,
                "project_irr_percent": feasibility.irr_percent
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

# ==========================================
# TAB 5: HELIOPOLIS_DNN SWIGLU INFERENCE
# ==========================================
with tabs[4]:
    st.markdown('<div class="brand-name" style="margin-bottom: 0.5rem;">HeliopolisDNN: PyTorch SwiGLU Multi-Task Inference</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.8rem; margin-bottom: 1.25rem;">Execute live neural-network inference to predict both structural Site Feasibility Probability and Optimized Levelized Cost of Electricity (LCOE) based on normalized multi-dimensional land/grid features.</div>', unsafe_allow_html=True)

    # Pre-populate physical features for input
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        feat_area = st.number_input("Inference Feature: Converted Area (sqm)", value=float(sq_meters), format="%.2f")
        feat_grid_dist = st.slider("Inference Feature: Upstream Substation Distance (km)", 0.2, 20.0, float(st.session_state.get("in_grid_dist", 2.5)), 0.1)
    with col_feat2:
        feat_mean_slope = st.number_input("Inference Feature: Mean Slope (deg)", value=float(terrain_model.mean_slope_degrees), format="%.2f")
        feat_owners_count = st.slider("Inference Feature: Registered Landowners Count", 1, 20, int(st.session_state.get("in_owners_count", len(owners_list))))
    with col_feat3:
        feat_max_slope = st.number_input("Inference Feature: Maximum Slope (deg)", value=float(st.session_state.get("in_max_slope", terrain_model.mean_slope_degrees * 1.8)), format="%.2f")
        # Dynamically resolve default GHI based on the active state
        default_ghi = 1550.0
        weather_path = os.path.join(os.path.dirname(__file__), "real_malaysian_weather.json")
        if os.path.exists(weather_path):
            try:
                with open(weather_path, "r", encoding="utf-8") as f:
                    weather_data = json.load(f)
                # Find matching state
                for key, val in weather_data.items():
                    if in_state.lower() in key.lower():
                        default_ghi = float(val["annual_ghi_kwh_m2_year"])
                        break
            except Exception:
                pass
        feat_ghi = st.number_input("Inference Feature: Solar GHI (kWh/m²/year)", value=float(default_ghi), step=10.0)

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    run_btn = st.button("🧠 Run Neural Site Feasibility Inference", use_container_width=True, type="primary")

    if run_btn:
        with st.spinner("Processing multi-task neural network forward pass..."):
            raw_features = np.array([[feat_area, feat_mean_slope, feat_max_slope, feat_grid_dist, float(feat_owners_count), feat_ghi]])
            try:
                prob_val, lcoe_val = dnn_inference(raw_features)

                # Present results beautifully
                c_inf1, c_inf2 = st.columns(2)
                with c_inf1:
                    badge_inf_cls = "badge-green" if prob_val >= 75.0 else ("badge-amber" if prob_val >= 35.0 else "badge-red")
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div class="metric-label">Predicted Feasibility Probability</div>
                        <div style="font-size: 2.5rem; font-weight: 800; margin: 0.8rem 0; color: var(--text);">{prob_val:.2f}%</div>
                        <span class="badge {badge_inf_cls}" style="font-size: 0.8rem;">{("FEASIBLE" if prob_val >= 75.0 else ("MARGINAL" if prob_val >= 35.0 else "UNFEASIBLE"))}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with c_inf2:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div class="metric-label">Predicted Levelized Cost of Electricity (LCOE)</div>
                        <div style="font-size: 2.5rem; font-weight: 800; margin: 0.8rem 0; color: var(--text);">RM {lcoe_val:.4f}</div>
                        <span class="badge badge-blue" style="font-size: 0.8rem;">PER kWh</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("""
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 1rem; text-align: center;">
                    *HeliopolisDNN features Swish-Gated Linear Units (SwiGLU) for continuous regression on LCOE parameters and binary classification on structural feasibility constraints.
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Inference execution failed: {e}")
