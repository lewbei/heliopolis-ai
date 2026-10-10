"""Strict, offline CSV reader for complete Malaysian billing-period load/PV profiles.

This parser does not fetch or fabricate a customer's demand data. A profile must
cover an entire user-declared billing period at one constant MYT interval rate.
"""
from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta

from solar_atap_settlement import IntervalEnergy, aggregate_aligned_intervals


def parse_billing_profile(
    csv_bytes: bytes,
    billing_days: int,
    interval_minutes: int = 30,
) -> IntervalEnergy:
    """Parse timestamp_myt,load_kwh,pv_kwh for an entire period starting 00:00 MYT.

    All timestamps must be ordered, unique and gap-free (30 or 60-minute slots).
    The profile is user-supplied/unverified; no unsupported annual extrapolation.
    """
    if type(billing_days) is not int or not 1 <= billing_days <= 62:
        raise ValueError("Billing days must be 1–62.")
    if interval_minutes not in (30, 60) or type(interval_minutes) is not int:
        raise ValueError("Interval length must be exactly 30 or 60 minutes.")
    if not isinstance(csv_bytes, bytes) or len(csv_bytes) > 2_000_000:
        raise ValueError("Upload a UTF-8 CSV smaller than 2 MB.")
    try:
        contents = csv_bytes.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must use UTF-8 text encoding.") from exc
    rows = csv.DictReader(io.StringIO(contents))
    required = ("timestamp_myt", "load_kwh", "pv_kwh")
    if rows.fieldnames != list(required):
        raise ValueError("CSV columns must exactly be timestamp_myt,load_kwh,pv_kwh.")

    expected = billing_days * (24 * 60 // interval_minutes)
    timestamps = []
    loads = []
    pv = []
    for row in rows:
        if len(timestamps) >= expected:
            raise ValueError("More records than full billing-period intervals.")
        try:
            stamp = datetime.strptime(row["timestamp_myt"], "%Y-%m-%d %H:%M")
            load = float(row["load_kwh"])
            produced = float(row["pv_kwh"])
        except (TypeError, ValueError, KeyError, OverflowError) as exc:
            raise ValueError("Malformed timestamp or numeric energy value in CSV.") from exc
        if row.get(None) is not None:
            raise ValueError("Unexpected extra CSV columns.")
        timestamps.append(stamp)
        loads.append(load)
        pv.append(produced)

    if len(timestamps) != expected:
        raise ValueError(
            f"Incomplete billing-period profile: expected {expected} intervals, "
            f"received {len(timestamps)}."
        )
    first = timestamps[0]
    if first.hour or first.minute:
        raise ValueError("Profile must begin at 00:00 Malaysia time (MYT).")
    step = timedelta(minutes=interval_minutes)
    if any(t != first + step * i for i, t in enumerate(timestamps)):
        raise ValueError("Missing, duplicated or out-of-order timestamp intervals.")
    return aggregate_aligned_intervals(loads, pv)
