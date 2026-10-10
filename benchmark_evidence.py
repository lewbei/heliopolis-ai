"""Paired evaluator for independently labeled title/SLD screening experiments.

This script DOES NOT invoke Gemini or invent baseline predictions, reference
labels or experimental results. To claim performance, fill a human-reviewed
CSV with all three *actual*, matched method outputs and audit metadata.

Usage:
    python benchmark_evidence.py --template benchmark.csv
    python benchmark_evidence.py --input benchmark.csv --output results.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

SYSTEMS = ("B0_DIRECT_VISION", "B1_SIMPLE_RULES", "H_HELIOPOLIS")
PREDICTIONS = ("FLAG", "CLEAR", "ABSTAIN", "ERROR")
SOURCE_TYPES = ("SYNTHETIC", "REAL")
REFERENCE_TYPES = ("FIXTURE", "INDEPENDENT_EXPERT")
DOMAINS = ("TITLE", "SLD")
SPLITS = ("DEVELOPMENT", "HOLDOUT")
COLUMNS = (
    "case_id", "domain", "split", "source_type", "reference_type",
    "input_sha256", "critical_issue", "system", "prediction",
    "model_id", "latency_ms", "api_calls", "usd_cost",
)


def write_empty_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fp:
        csv.writer(fp).writerow(COLUMNS)


def _num(name: str, value: str | None, *, integer: bool = False) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        number = int(value) if integer else float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid {name}: {value!r}") from exc
    if isinstance(number, bool) or not math.isfinite(number) or number < 0:
        raise ValueError(f"{name} must be nonnegative and finite.")
    return number


def read_pairs(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        if not reader.fieldnames or any(field not in reader.fieldnames for field in COLUMNS):
            raise ValueError(f"CSV must include all required columns: {', '.join(COLUMNS)}")
        rows = list(reader)

    if not rows:
        raise ValueError("No observed evaluation data. Do not invent a benchmark.")
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        case_id = row["case_id"].strip()
        if not case_id or any(not (row.get(key) or "").strip() for key in COLUMNS[:10]):
            raise ValueError("Each row needs a case ID and complete source/reference/model metadata.")
        for name, allowed in (
            ("domain", DOMAINS), ("split", SPLITS),
            ("source_type", SOURCE_TYPES), ("reference_type", REFERENCE_TYPES),
            ("system", SYSTEMS), ("prediction", PREDICTIONS),
        ):
            if row[name] not in allowed:
                raise ValueError(f"Invalid {name} for {case_id}: {row[name]!r}")
        if row["critical_issue"] not in ("0", "1"):
            raise ValueError("critical_issue must be 0 or 1, independent of model output.")
        if row["source_type"] == "REAL" and row["reference_type"] != "INDEPENDENT_EXPERT":
            raise ValueError("Real-document results require an independently annotated reference.")
        if row["source_type"] == "SYNTHETIC" and row["reference_type"] != "FIXTURE":
            raise ValueError("Synthetic cases cannot claim independently verified ground truth.")
        if len(row["input_sha256"]) != 64 or any(
            char not in "0123456789abcdef" for char in row["input_sha256"].lower()
        ):
            raise ValueError("input_sha256 must be an SHA-256 digest of the shared document/input.")
        row["latency_ms"] = _num("latency_ms", row["latency_ms"])
        row["api_calls"] = _num("api_calls", row["api_calls"], integer=True)
        row["usd_cost"] = _num("usd_cost", row["usd_cost"])
        by_case[case_id].append(row)

    for case_id, group in by_case.items():
        if len(group) != len(SYSTEMS) or {r["system"] for r in group} != set(SYSTEMS):
            raise ValueError(
                f"{case_id}: require exactly one B0, B1 and H prediction on matched input."
            )
        for key in ("domain", "split", "source_type", "reference_type", "critical_issue", "input_sha256", "model_id"):
            if len({r[key] for r in group}) != 1:
                raise ValueError(f"{case_id}: mismatched {key} across compared methods.")

    return rows


def evaluate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("No benchmark records.")
    cases = {row["case_id"] for row in rows}
    real = any(row["source_type"] == "REAL" for row in rows)
    result = {
        "scope": (
            "PAIRED_OBSERVATIONS_WITH_REAL_DOCUMENTS" if real
            else "SYNTHETIC_EVALUATOR_CHECK_NOT_REAL_WORLD_ACCURACY"
        ),
        "cases": len(cases),
        "total_system_rows": len(rows),
        "methods": {},
        "warnings": [
            "FLAG means the method raised a modeled critical finding; CLEAR is only "
            "a screening output, never legal/utility approval.",
            "ABSTAIN and ERROR are not counted as a correct detection or a true negative.",
            "A direct-Vision B0 also needs a fair fixed prompt, matching input and "
            "cost/time accounting; this script does not run it.",
            "No independent field accuracy can be claimed from SYNTHETIC fixtures.",
        ],
    }
    for split in SPLITS:
        for source in SOURCE_TYPES:
            cohort = [r for r in rows if r["split"] == split and r["source_type"] == source]
            if not cohort:
                continue
            group_name = f"{split}_{source}"
            result["methods"][group_name] = {}
            for system in SYSTEMS:
                group = [r for r in cohort if r["system"] == system]
                positives = [r for r in group if r["critical_issue"] == "1"]
                negatives = [r for r in group if r["critical_issue"] == "0"]
                flagged = sum(r["prediction"] == "FLAG" for r in positives)
                missed = sum(r["prediction"] == "CLEAR" for r in positives)
                abstained = sum(r["prediction"] == "ABSTAIN" for r in group)
                errors = sum(r["prediction"] == "ERROR" for r in group)
                known_good_flagged = sum(r["prediction"] == "FLAG" for r in negatives)
                decision_count = sum(r["prediction"] in ("FLAG", "CLEAR") for r in group)
                latencies = [r["latency_ms"] for r in group if r["latency_ms"] is not None]
                calls = [r["api_calls"] for r in group if r["api_calls"] is not None]
                costs = [r["usd_cost"] for r in group if r["usd_cost"] is not None]
                result["methods"][group_name][system] = {
                    "n": len(group),
                    "critical_cases": len(positives),
                    "noncritical_cases": len(negatives),
                    "critical_flags": flagged,
                    "false_clearance_on_critical_cases": missed,
                    "false_clearance_rate_on_critical_cases": (
                        missed / len(positives) if positives else None
                    ),
                    "critical_flag_fraction": flagged / len(positives) if positives else None,
                    "noncritical_false_flags": known_good_flagged,
                    "abstentions": abstained,
                    "errors": errors,
                    "decision_coverage": decision_count / len(group),
                    "latency_measured_n": len(latencies),
                    "median_latency_ms": median(latencies) if latencies else None,
                    "api_calls_measured_n": len(calls),
                    "total_api_calls": sum(calls) if len(calls) == len(group) else None,
                    "cost_measured_n": len(costs),
                    "total_cost_usd": sum(costs) if len(costs) == len(group) else None,
                }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--template", type=Path)
    group.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.template:
        write_empty_template(args.template)
        print("Created empty template. No predictions or reference labels were fabricated.")
        return
    result = evaluate(read_pairs(args.input))
    formatted = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(formatted + "\n", encoding="utf-8")
    print(formatted)


if __name__ == "__main__":
    main()
