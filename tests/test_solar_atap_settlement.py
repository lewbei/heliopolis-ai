"""Pure Solar ATAP GP/ST/No.60/2025 non-domestic settlement checks.

Only synthetic/unit fixtures here. Not bill validation, legal approval or ROI.
"""

from dataclasses import replace
import math

import pytest

from solar_atap_settlement import (
    NonDomesticBillingPeriod,
    aggregate_aligned_intervals,
    settle_non_domestic_month,
)


def _month(**updates):
    example = NonDomesticBillingPeriod(
        capacity_kwac=100.0,
        assumed_maximum_demand_kw=150.0,
        billing_days=30,
        grid_import_kwh=12000.0,
        grid_export_kwh=20000.0,
        prevailing_energy_charge_rm_per_kwh=0.40,
        # Single Buyer's *revised* January 2026 illustrative published SMP
        # for the next (February) month; not a current 2026 forecast.
        average_smp_rm_per_kwh=0.1911,
        contract_month=2,
        billing_month="2026-02",
        smp_reference_month="2026-01",
        input_basis="SYNTHETIC_FIXTURE",
    )
    return replace(example, **updates)


def test_maq_and_import_limits_are_applied_before_cash_value():
    x = settle_non_domestic_month(_month())
    assert x.max_allowable_quantity_kwh == pytest.approx(15000.0)
    assert x.eligible_export_kwh == pytest.approx(12000.0)
    assert x.forfeited_export_kwh == pytest.approx(8000.0)
    assert x.import_energy_charge_rm == pytest.approx(4800.0)
    assert x.applied_export_credit_rm == pytest.approx(2293.2)
    assert x.net_import_energy_charge_rm == pytest.approx(2506.8)
    assert x.status == "ILLUSTRATIVE_ATAP_ENERGY_ONLY"


def test_export_limited_by_maq_even_with_large_import():
    x = settle_non_domestic_month(_month(grid_import_kwh=30000))
    assert x.eligible_export_kwh == pytest.approx(15000)
    assert x.forfeited_export_kwh == pytest.approx(5000)


def test_no_rollover_no_cash_payment_bill_floors_at_zero():
    x = settle_non_domestic_month(
        _month(
            capacity_kwac=1.0, assumed_maximum_demand_kw=5.0,
            billing_days=1, grid_import_kwh=10.0, grid_export_kwh=100.0,
            prevailing_energy_charge_rm_per_kwh=0.10,
            average_smp_rm_per_kwh=0.50,
        )
    )
    assert x.eligible_export_kwh == pytest.approx(5.0)
    assert x.applied_export_credit_rm == pytest.approx(1.0)
    assert x.unused_credit_value_rm == pytest.approx(1.5)
    assert x.net_import_energy_charge_rm == 0.0
    assert x.forfeited_export_kwh == pytest.approx(95.0)


def test_no_import_means_no_export_credit_even_with_solar_surplus():
    x = settle_non_domestic_month(_month(grid_import_kwh=0.0))
    assert x.eligible_export_kwh == 0.0
    assert x.applied_export_credit_rm == 0.0
    assert x.forfeited_export_kwh == 20000.0


@pytest.mark.parametrize("year_month,price_month", [
    ("2026-02", "2026-02"),
    ("2026-02", "2025-12"),
    ("2026-01", "2026-01"),
    ("2026-15", "2026-14"),
])
def test_wrong_or_invalid_average_smp_period_is_rejected(year_month, price_month):
    with pytest.raises(ValueError):
        settle_non_domestic_month(
            _month(billing_month=year_month, smp_reference_month=price_month)
        )


def test_missing_smp_or_provenance_fails_closed():
    with pytest.raises(ValueError, match="Average SMP"):
        settle_non_domestic_month(_month(average_smp_rm_per_kwh=None))
    with pytest.raises(ValueError, match="YYYY-MM"):
        settle_non_domestic_month(_month(smp_reference_month=None))


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.5])
def test_unsafe_smp_values_rejected(value):
    with pytest.raises(ValueError):
        settle_non_domestic_month(_month(average_smp_rm_per_kwh=value))


@pytest.mark.parametrize("kw,md", [(1000.01, 2000.0), (400.0, 300.0), (0.0, 100.0)])
def test_capacity_requires_both_nominal_cap_and_md(kw, md):
    with pytest.raises(ValueError):
        settle_non_domestic_month(
            _month(capacity_kwac=kw, assumed_maximum_demand_kw=md)
        )


def test_ten_year_boundary_and_post_term_strict_self_consumption():
    x = settle_non_domestic_month(_month(contract_month=120))
    assert x.export_credit_applies is True
    assert x.applied_export_credit_rm > 0
    with pytest.raises(ValueError, match="strictly self-consumption"):
        settle_non_domestic_month(_month(contract_month=121))
    y = settle_non_domestic_month(
        _month(
            contract_month=121, grid_export_kwh=0.0,
            average_smp_rm_per_kwh=None,
            billing_month=None, smp_reference_month=None,
        )
    )
    assert y.export_credit_applies is False
    assert y.applied_export_credit_rm == 0.0
    assert y.status == "POST_TEN_YEAR_SELF_CONSUMPTION_ONLY"


def test_only_aligned_profiles_can_infer_on_site_self_consumption():
    total = aggregate_aligned_intervals(
        customer_load_kwh=[5.0, 0.0, 3.0],
        solar_generation_kwh=[3.0, 4.0, 7.0],
    )
    assert total.base_load_kwh == 8.0
    assert total.solar_generated_kwh == 14.0
    assert total.on_site_solar_kwh == 6.0
    assert total.grid_import_kwh == 2.0
    assert total.grid_export_kwh == 8.0


def test_invalid_intervals_are_not_accepted():
    with pytest.raises(ValueError):
        aggregate_aligned_intervals([1, 2], [1])
    with pytest.raises(ValueError):
        aggregate_aligned_intervals([1, math.nan], [1, 1])
    with pytest.raises(ValueError):
        aggregate_aligned_intervals([], [])


def test_user_supplied_data_cannot_claim_independent_verification():
    with pytest.raises(ValueError, match="verified"):
        settle_non_domestic_month(_month(input_basis="VERIFIED_PRODUCTION"))
