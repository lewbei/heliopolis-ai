"""Synthetic metric arithmetic tests, NOT a Heliopolis accuracy/latency benchmark."""

import csv
import hashlib
from pathlib import Path

import pytest

from benchmark_evidence import COLUMNS, SYSTEMS, evaluate, read_pairs, write_empty_template


def _row(case, critical, system, prediction, **override):
    base = {
        "case_id": case, "domain": "SLD", "split": "HOLDOUT",
        "source_type": "SYNTHETIC", "reference_type": "FIXTURE",
        "input_sha256": hashlib.sha256(case.encode()).hexdigest(),
        "critical_issue": str(critical), "system": system,
        "prediction": prediction, "model_id": "same-imaginary-model",
        "latency_ms": "", "api_calls": "", "usd_cost": "",
    }
    base.update(override)
    return base


def _write(tmp_path: Path, rows: list[dict]):
    path = tmp_path / "observed.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_empty_template_has_no_fabricated_predictions(tmp_path):
    path = tmp_path / "template.csv"
    write_empty_template(path)
    with pytest.raises(ValueError, match="No observed"):
        read_pairs(path)
    assert len(path.read_text().splitlines()) == 1


def test_pairwise_metrics_do_not_count_abstention_as_correct(tmp_path):
    cases = [
        _row("critical-1", 1, "B0_DIRECT_VISION", "CLEAR"),
        _row("critical-1", 1, "B1_SIMPLE_RULES", "ABSTAIN"),
        _row("critical-1", 1, "H_HELIOPOLIS", "FLAG"),
        _row("noncritical-2", 0, "B0_DIRECT_VISION", "CLEAR"),
        _row("noncritical-2", 0, "B1_SIMPLE_RULES", "CLEAR"),
        _row("noncritical-2", 0, "H_HELIOPOLIS", "ABSTAIN"),
    ]
    result = evaluate(read_pairs(_write(tmp_path, cases)))
    assert result["scope"] == "SYNTHETIC_EVALUATOR_CHECK_NOT_REAL_WORLD_ACCURACY"
    assert result["cases"] == 2
    scores = result["methods"]["HOLDOUT_SYNTHETIC"]
    assert scores["B0_DIRECT_VISION"]["false_clearance_on_critical_cases"] == 1
    assert scores["B1_SIMPLE_RULES"]["abstentions"] == 1
    assert scores["B1_SIMPLE_RULES"]["critical_flag_fraction"] == 0.0
    assert scores["H_HELIOPOLIS"]["critical_flags"] == 1
    assert scores["H_HELIOPOLIS"]["decision_coverage"] == 0.5
    assert scores["H_HELIOPOLIS"]["median_latency_ms"] is None
    assert scores["H_HELIOPOLIS"]["total_cost_usd"] is None


def test_incomplete_three_method_comparison_refused(tmp_path):
    cases = [_row("x", 1, "B1_SIMPLE_RULES", "CLEAR"), _row("x", 1, "H_HELIOPOLIS", "FLAG")]
    with pytest.raises(ValueError, match="exactly one"):
        read_pairs(_write(tmp_path, cases))


def test_duplicate_method_or_mismatched_reference_refused(tmp_path):
    rows = [_row("x", 1, m, "ABSTAIN") for m in SYSTEMS]
    rows[1]["system"] = "B0_DIRECT_VISION"
    with pytest.raises(ValueError, match="exactly one"):
        read_pairs(_write(tmp_path, rows))
    rows = [_row("x", 1, m, "ABSTAIN") for m in SYSTEMS]
    rows[1]["critical_issue"] = "0"
    with pytest.raises(ValueError, match="mismatched critical_issue"):
        read_pairs(_write(tmp_path, rows))


def test_real_document_without_independent_expert_label_refused(tmp_path):
    rows = [
        _row("x", 1, m, "FLAG", source_type="REAL", reference_type="FIXTURE")
        for m in SYSTEMS
    ]
    with pytest.raises(ValueError, match="independently annotated"):
        read_pairs(_write(tmp_path, rows))


@pytest.mark.parametrize("field,bad", [
    ("input_sha256", "abc"),
    ("prediction", "APPROVED"),
    ("model_id", ""),
    ("latency_ms", "-1"),
    ("api_calls", "NaN"),
    ("usd_cost", "-3"),
])
def test_invalid_evidence_values_rejected(tmp_path, field, bad):
    rows = [_row("x", 1, m, "ABSTAIN") for m in SYSTEMS]
    rows[0][field] = bad
    with pytest.raises(ValueError):
        read_pairs(_write(tmp_path, rows))


def test_mismatched_vision_model_is_not_fair_baseline(tmp_path):
    rows = [_row("x", 1, m, "ABSTAIN") for m in SYSTEMS]
    rows[2]["model_id"] = "larger-paid-model"
    with pytest.raises(ValueError, match="mismatched model_id"):
        read_pairs(_write(tmp_path, rows))


def test_latency_and_cost_are_only_reported_when_measured(tmp_path):
    rows = [
        _row("x", 0, m, "CLEAR", latency_ms="10.5", api_calls="1", usd_cost="0.001")
        for m in SYSTEMS
    ]
    rows[2]["usd_cost"] = ""
    reports = evaluate(read_pairs(_write(tmp_path, rows)))
    group = reports["methods"]["HOLDOUT_SYNTHETIC"]
    assert group["B0_DIRECT_VISION"]["median_latency_ms"] == 10.5
    assert group["B0_DIRECT_VISION"]["total_api_calls"] == 1
    assert group["B0_DIRECT_VISION"]["total_cost_usd"] == 0.001
    assert group["H_HELIOPOLIS"]["total_cost_usd"] is None
    assert group["H_HELIOPOLIS"]["cost_measured_n"] == 0
