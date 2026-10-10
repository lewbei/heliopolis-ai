"""Separate Solar ATAP non-domestic monthly screen — NOT the utility-scale LSS app.

Run via the Streamlit pages sidebar from app.py, or
streamlit run pages/1_Solar_ATAP_Monthly.py.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atap_profile_io import parse_billing_profile
from solar_atap_settlement import (
    GUIDELINE_URL,
    SMP_SOURCE_URL,
    NonDomesticBillingPeriod,
    settle_non_domestic_month,
)

st.set_page_config(page_title="Solar ATAP monthly energy screen", layout="wide")

st.title("Solar ATAP — monthly energy-only screening")
st.caption(
    "Non-domestic consumer rooftop / solar carpark installation. "
    "Distinct from Heliopolis utility-scale LSS land prospecting."
)
st.warning(
    "PRELIMINARY ESTIMATE ONLY: no verified TNB connection/consumer eligibility, "
    "complete utility bill, grid approval, signed tariff, banking or investment advice. "
    "No real customer data or API credentials are included."
)

st.markdown(
    "Under Energy Commission GP/ST/No.60/2025, the export credit uses the prior "
    "calendar month's **daytime Average SMP**, and credited export cannot exceed "
    "measured exports, the monthly MAQ or imported energy. Unused credits are "
    "forfeited. This page never reuses a historical NOVA energy tariff as Solar ATAP."
)
st.link_button("Energy Commission official guideline", GUIDELINE_URL)
st.link_button("Single Buyer — monthly SMP", SMP_SOURCE_URL)

mode = st.radio(
    "Evidence mode",
    [
        "Manual billing totals — user supplied, not independently verified",
        "Full interval CSV — user supplied, not independently verified",
        "Clearly synthetic MAIC judge fixture",
    ],
    horizontal=False,
)
synthetic = mode.startswith("Clearly synthetic")
interval_mode = mode.startswith("Full interval")

with st.form("atap_monthly_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        capacity = st.number_input(
            "Inverter AC rating (kWac)", min_value=0.0,
            value=100.0 if synthetic else 0.0, step=10.0
        )
        md = st.number_input(
            "Provided customer Maximum Demand (kW) — unverified",
            min_value=0.0, value=150.0 if synthetic else 0.0, step=10.0,
        )
        days = st.number_input(
            "Billing period days", min_value=1, max_value=62,
            value=30 if synthetic else 30, step=1,
        )
    with c2:
        month = st.text_input(
            "Billing month YYYY-MM", value="2026-02" if synthetic else "",
            placeholder="2026-10",
        )
        smp_month = st.text_input(
            "PRECEDING SMP reference month YYYY-MM",
            value="2026-01" if synthetic else "",
            placeholder="2026-09",
        )
        contract_month = st.number_input(
            "ATAP contract month (1–120; >120 is post-ATAP)",
            min_value=1, value=2 if synthetic else 1, step=1,
        )
    with c3:
        energy_rate = st.number_input(
            "Provided energy charge (RM/kWh) — NOT total retail tariff",
            min_value=0.0, value=0.40 if synthetic else 0.0,
            format="%.4f", step=0.01,
        )
        smp_str = st.text_input(
            "Published Average SMP from prior month (RM/kWh)",
            value="0.1911" if synthetic else "",
            placeholder="Enter official published rate; no auto-fallback",
        )
        st.caption(
            "Synthetic example uses Single Buyer's revised Jan 2026 SMP, "
            "NOT today's SMP or a guaranteed future export price."
        )

    source_details = None
    if interval_mode:
        uploaded = st.file_uploader(
            "Complete time-aligned load/PV profile CSV",
            type=["csv"],
            help="Exactly timestamp_myt,load_kwh,pv_kwh; 30 or 60 min intervals; "
                 "one full billing period beginning at 00:00 MYT, no missing steps.",
        )
        slot = st.selectbox("Profile interval length (minutes)", [30, 60])
        st.caption(
            "The upload is used only to calculate totals during this run. "
            "Do not upload personal identifiers or confidential data without permission."
        )
        import_kwh = export_kwh = 0.0
    else:
        a, b = st.columns(2)
        with a:
            import_kwh = st.number_input(
                "Grid IMPORT kWh (for one billing period)", min_value=0.0,
                value=12000.0 if synthetic else 0.0, step=100.0,
            )
        with b:
            export_kwh = st.number_input(
                "Grid EXPORT kWh (for same billing period)", min_value=0.0,
                value=20000.0 if synthetic else 0.0, step=100.0,
            )
    submitted = st.form_submit_button("Calculate energy-only monthly screening")

if submitted:
    try:
        if interval_mode:
            if uploaded is None:
                raise ValueError("Upload a complete time-aligned billing profile.")
            profile = parse_billing_profile(
                uploaded.getvalue(),
                billing_days=int(days),
                interval_minutes=int(slot),
            )
            import_kwh, export_kwh = profile.grid_import_kwh, profile.grid_export_kwh
            source_details = asdict(profile)

        average_smp = None if not smp_str.strip() else float(smp_str.strip())
        record = NonDomesticBillingPeriod(
            capacity_kwac=float(capacity),
            assumed_maximum_demand_kw=float(md),
            billing_days=int(days),
            grid_import_kwh=float(import_kwh),
            grid_export_kwh=float(export_kwh),
            prevailing_energy_charge_rm_per_kwh=float(energy_rate),
            average_smp_rm_per_kwh=average_smp,
            contract_month=int(contract_month),
            billing_month=month.strip() or None,
            smp_reference_month=smp_month.strip() or None,
            input_basis=(
                "SYNTHETIC_FIXTURE" if synthetic else "USER_SUPPLIED_UNVERIFIED"
            ),
        )
        result = settle_non_domestic_month(record)
    except (ValueError, TypeError, UnicodeDecodeError) as exc:
        st.error(f"NEEDS_REVIEW / missing required evidence: {exc}")
        st.stop()

    st.subheader("Monthly result — energy component only")
    if synthetic:
        st.warning("SYNTHETIC MAIC EXAMPLE — NOT measured TNB customer data.")
    else:
        st.warning("USER-PROVIDED DATA — not independently checked against TNB records.")

    x, y, z = st.columns(3)
    x.metric("Maximum Allowable Quantity", f"{result.max_allowable_quantity_kwh:,.2f} kWh")
    y.metric("Creditable export quantity", f"{result.eligible_export_kwh:,.2f} kWh")
    z.metric("Forfeited export", f"{result.forfeited_export_kwh:,.2f} kWh")
    a, b, c = st.columns(3)
    a.metric("Energy-charge subtotal (before credit)", f"RM {result.import_energy_charge_rm:,.2f}")
    b.metric("Applied export energy credit", f"RM {result.applied_export_credit_rm:,.2f}")
    c.metric("Energy charge after credit", f"RM {result.net_import_energy_charge_rm:,.2f}")
    st.caption(
        "These are energy-charge components, NOT the complete TNB bill or bill savings. "
        "AFA, KWTBB, SST, demand charges, rebates, account conditions and network studies "
        "are not evaluated. Contract month 1–120 is a simplified term check; "
        "actual commencement/expiry dates must be verified independently."
    )

    report = {
        "report_status": result.status,
        "scope": "NON_DOMESTIC_ATAP_ENERGY_ONLY_NOT_TNB_INVOICE_OR_ROI",
        "data_provenance": record.input_basis,
        "independent_verification": False,
        "mode": mode,
        "user_inputs": asdict(record),
        "time_aligned_profile_totals": source_details,
        "calculated_energy_only_result": asdict(result),
        "does_not_certify": [
            "Actual programme acceptance",
            "Consumer maximum demand verification",
            "TNB invoice, total savings or cash payout",
            "Eligible grid connection or engineering approval",
            "Annual/bankable NPV or IRR",
        ],
    }
    st.download_button(
        "Download preliminary monthly audit (JSON)",
        data=json.dumps(report, indent=2),
        mime="application/json",
        file_name="solar_atap_monthly_preliminary.json",
    )
