"""Solar ATAP non-domestic energy-component screening, not an invoice or ROI model.

Authority: Energy Commission GP/ST/No. 60/2025 (effective 1 January 2026),
sections 2 (MAQ and Average SMP), 3.6, 4, 8, 13 and 14.

This model MUST receive actual or explicitly synthetic period measurements
and a separately sourced monthly Average SMP. It does not invent tariffs,
forecast load, guarantee contract eligibility, or model non-energy charges.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

GUIDELINE_URL = (
    "https://www.st.gov.my/sites/default/files/2026-03/"
    "GUIDELINES-FOR-SOLAR-ACCELERATED_0.pdf"
)
SMP_SOURCE_URL = (
    "https://www.singlebuyer.com.my/market/market-data/system-marginal-price"
)


def _nonnegative_number(label: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{label} must be numeric.")
    x = float(value)
    if not isfinite(x) or x < 0:
        raise ValueError(f"{label} must be finite and nonnegative.")
    return x


@dataclass(frozen=True)
class IntervalEnergy:
    """Totals from time-aligned load and PV generation energy intervals (kWh)."""

    base_load_kwh: float
    solar_generated_kwh: float
    on_site_solar_kwh: float
    grid_import_kwh: float
    grid_export_kwh: float
    evidence_status: str = "USER_SUPPLIED_OR_SYNTHETIC_UNVERIFIED"


def aggregate_aligned_intervals(
    customer_load_kwh: Sequence[float],
    solar_generation_kwh: Sequence[float],
) -> IntervalEnergy:
    """Split coincident PV consumption and excess export at the same meter intervals.

    Both sequences MUST use identical time windows and time zones. Annual or
    monthly unaligned totals cannot determine self-consumption accurately.
    No storage/charging/discharging, curtailment or grid export constraints
    are modeled here.
    """
    loads, solar = tuple(customer_load_kwh), tuple(solar_generation_kwh)
    if not loads or len(loads) != len(solar):
        raise ValueError("Provide equal nonempty, time-aligned load/PV sequences.")

    totals = dict(load=0.0, solar=0.0, onsite=0.0, imported=0.0, exported=0.0)
    for l, g in zip(loads, solar):
        l = _nonnegative_number("Load interval", l)
        g = _nonnegative_number("PV interval", g)
        totals["load"] += l
        totals["solar"] += g
        totals["onsite"] += min(l, g)
        totals["imported"] += max(l - g, 0.0)
        totals["exported"] += max(g - l, 0.0)

    return IntervalEnergy(
        base_load_kwh=totals["load"],
        solar_generated_kwh=totals["solar"],
        on_site_solar_kwh=totals["onsite"],
        grid_import_kwh=totals["imported"],
        grid_export_kwh=totals["exported"],
    )


@dataclass(frozen=True)
class NonDomesticBillingPeriod:
    """User-supplied inputs for ONE monthly billing period, not an eligibility certificate."""

    capacity_kwac: float
    assumed_maximum_demand_kw: float
    billing_days: int
    grid_import_kwh: float
    grid_export_kwh: float
    prevailing_energy_charge_rm_per_kwh: float
    average_smp_rm_per_kwh: float | None
    contract_month: int  # 1..120 = within ATAP; >=121 strictly self-consumption
    smp_reference_month: str | None = None
    input_basis: str = "USER_SUPPLIED_UNVERIFIED"


@dataclass(frozen=True)
class NonDomesticMonthlyResult:
    status: str
    max_allowable_quantity_kwh: float
    eligible_export_kwh: float
    forfeited_export_kwh: float
    import_energy_charge_rm: float
    applied_export_credit_rm: float
    unused_credit_value_rm: float
    net_import_energy_charge_rm: float
    export_credit_applies: bool
    source_url: str = GUIDELINE_URL
    smp_source_url: str = SMP_SOURCE_URL
    excluded_from_model: str = (
        "Actual TNB invoice, AFA, SST, KWTBB, demand/fixed charges, "
        "bill incentives, battery dispatch, current eligibility and 21-year ROI"
    )


def settle_non_domestic_month(
    record: NonDomesticBillingPeriod,
) -> NonDomesticMonthlyResult:
    """Energy-only Solar ATAP bill-offset rule under EXPLICIT hypothetical eligibility.

    Credit is limited per billing month by the least of metered export, MAQ,
    and import kWh, and then by the gross import-energy charge. Unused
    energy/credits are forfeited; no cash transfer or month-to-month rollover.

    Returns a modelled energy charge, not a complete electricity bill.
    """
    capacity = _nonnegative_number("AC capacity", record.capacity_kwac)
    md = _nonnegative_number("Maximum demand", record.assumed_maximum_demand_kw)
    imported = _nonnegative_number("Grid import", record.grid_import_kwh)
    exported = _nonnegative_number("Grid export", record.grid_export_kwh)
    rate = _nonnegative_number(
        "Prevailing energy charge", record.prevailing_energy_charge_rm_per_kwh
    )
    if capacity <= 0 or md <= 0:
        raise ValueError("AC capacity and assumed MD must be positive.")
    if capacity > 1000 or capacity > md:
        raise ValueError(
            "Non-domestic Solar ATAP nominal cap is 1,000 kWac AND <=100% of MD. "
            "This does not establish eligibility."
        )
    if (
        isinstance(record.billing_days, bool)
        or not isinstance(record.billing_days, int)
        or not 1 <= record.billing_days <= 62
    ):
        raise ValueError("Billing period must be an actual positive day count.")
    if (
        isinstance(record.contract_month, bool)
        or not isinstance(record.contract_month, int)
        or record.contract_month <= 0
    ):
        raise ValueError("Contract month must be a positive integer.")
    if record.input_basis not in {"USER_SUPPLIED_UNVERIFIED", "SYNTHETIC_FIXTURE"}:
        raise ValueError("Do not assert independently verified inputs in this prototype.")

    in_atap_term = record.contract_month <= 120
    if not in_atap_term and exported > 0:
        raise ValueError(
            "After the 10-year ATAP term, strictly self-consumption is allowed. "
            "A nonzero export requires a separate curtailment/SELCO review."
        )
    if in_atap_term and record.average_smp_rm_per_kwh is None:
        raise ValueError(
            "Missing preceding-month Single Buyer Average SMP; never assume a "
            "flat NOVA or retail export tariff."
        )
    smp = (
        _nonnegative_number("Monthly Average SMP", record.average_smp_rm_per_kwh)
        if in_atap_term else 0.0
    )
    maq = capacity * 5.0 * record.billing_days
    eligible_kwh = min(exported, maq, imported) if in_atap_term else 0.0
    gross_energy_rm = imported * rate
    nominal_credit_rm = eligible_kwh * smp
    applied_rm = min(nominal_credit_rm, gross_energy_rm)
    return NonDomesticMonthlyResult(
        status=(
            "ILLUSTRATIVE_ATAP_ENERGY_ONLY"
            if in_atap_term else "POST_TEN_YEAR_SELF_CONSUMPTION_ONLY"
        ),
        max_allowable_quantity_kwh=maq,
        eligible_export_kwh=eligible_kwh,
        forfeited_export_kwh=max(0.0, exported - eligible_kwh),
        import_energy_charge_rm=gross_energy_rm,
        applied_export_credit_rm=applied_rm,
        unused_credit_value_rm=max(0.0, nominal_credit_rm - applied_rm),
        net_import_energy_charge_rm=max(0.0, gross_energy_rm - applied_rm),
        export_credit_applies=in_atap_term,
    )
