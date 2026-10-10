"""Synthetic input fixtures validating strict full-period ATAP CSV loading."""
import csv
import io
from datetime import datetime, timedelta

import pytest

from atap_profile_io import parse_billing_profile


def make_profile(days=1, step=30, missing=None, extra=False, bad=None):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp_myt", "load_kwh", "pv_kwh"])
    start = datetime(2026, 1, 1)
    slots = days * 24 * 60 // step
    for idx in range(slots + (1 if extra else 0)):
        if idx == missing:
            continue
        timestamp = (start + timedelta(minutes=idx * step)).strftime("%Y-%m-%d %H:%M")
        load, pv = 2.0, 3.0
        if idx == bad:
            pv = "not-a-number"
        writer.writerow([timestamp, load, pv])
    return output.getvalue().encode("utf-8")


def test_complete_halfhour_profile_exact_energy_totals():
    result = parse_billing_profile(make_profile(), billing_days=1)
    assert result.base_load_kwh == pytest.approx(96.0)
    assert result.solar_generated_kwh == pytest.approx(144.0)
    assert result.on_site_solar_kwh == pytest.approx(96.0)
    assert result.grid_import_kwh == 0
    assert result.grid_export_kwh == pytest.approx(48.0)
    assert "UNVERIFIED" in result.evidence_status


def test_complete_hour_profile_supported():
    result = parse_billing_profile(make_profile(step=60), billing_days=1, interval_minutes=60)
    assert result.grid_export_kwh == pytest.approx(24.0)


@pytest.mark.parametrize("csv_bytes,days", [
    (make_profile(missing=2), 1),
    (make_profile(extra=True), 1),
    (make_profile(), 2),
])
def test_incomplete_or_extra_period_is_rejected(csv_bytes, days):
    with pytest.raises(ValueError):
        parse_billing_profile(csv_bytes, billing_days=days)


def test_gap_is_rejected_even_with_unchanged_record_count():
    source = make_profile().decode("utf-8")
    source = source.replace("2026-01-01 01:00", "2026-01-01 01:15")
    with pytest.raises(ValueError, match="Missing"):
        parse_billing_profile(source.encode("utf-8"), billing_days=1)


def test_bad_energy_cell_is_rejected():
    with pytest.raises(ValueError):
        parse_billing_profile(make_profile(bad=7), billing_days=1)


@pytest.mark.parametrize("header", [
    "timestamp,load_kwh,pv_kwh",
    "timestamp_myt,solar_kwh,load_kwh",
])
def test_exact_column_schema_is_required(header):
    payload = make_profile().decode("utf-8")
    payload = payload.replace("timestamp_myt,load_kwh,pv_kwh", header, 1)
    with pytest.raises(ValueError, match="columns"):
        parse_billing_profile(payload.encode("utf-8"), 1)


def test_reject_negative_and_nonfinite_kwh():
    payload = make_profile().decode("utf-8")
    payload = payload.replace(",2.0,3.0", ",2.0,NaN", 1)
    with pytest.raises(ValueError):
        parse_billing_profile(payload.encode(), 1)
    payload = make_profile().decode("utf-8")
    payload = payload.replace(",2.0,3.0", ",-4.0,3.0", 1)
    with pytest.raises(ValueError):
        parse_billing_profile(payload.encode(), 1)


def test_no_fabricated_profile_for_small_or_bad_input():
    for data in (b"", b"\xff", b"bad"):
        with pytest.raises(ValueError):
            parse_billing_profile(data, 1)
    with pytest.raises(ValueError):
        parse_billing_profile(make_profile(), 0)
    with pytest.raises(ValueError):
        parse_billing_profile(make_profile(), 1, 45)
