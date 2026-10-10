# MAIC evaluation — reproducible paired baseline protocol

**Status:** evaluator implemented, **not a completed field benchmark**. Repository contains no consented real land titles, independent SLD labels, customer billing records or live Gemini API outputs. Do not report a real accuracy number from unit tests.

## Methods to compare on the SAME input

- **B0_DIRECT_VISION:** Direct Gemini response/field extraction baseline. This must be executed, not invented.
- **B1_SIMPLE_RULES:** Same Gemini model and source, followed by a minimal checklist/standard spreadsheet check.
- **H_HELIOPOLIS:** Same Gemini model and source, followed by Heliopolis's actual validations.

All three must have actually run under comparable model, prompt and token/time/cost budgets. If evaluating only post-processing, share one cached extraction across B1/H, and disclose it. Do not pretend cached predictions are independent OCR successes.

## Data collection and comparison

Generate an empty local CSV schema:

    python benchmark_evidence.py --template PRIVATE_matched_results.csv

Required columns are case_id, domain, split, source_type, reference_type, input_sha256, critical_issue, system, prediction, model_id, latency_ms, api_calls, usd_cost. The last three may be blank (they remain null, not fabricated zero).

- domain: TITLE / SLD; split: DEVELOPMENT / HOLDOUT.
- source_type: REAL / SYNTHETIC. reference_type: INDEPENDENT_EXPERT for REAL; FIXTURE for SYNTHETIC. The evaluator rejects a real example labeled solely by the model being tested.
- input_sha256: common SHA-256 digest for the same document/input, identical across all three methods. Do not publish PII or the original source.
- critical_issue: 1 if a blinded expert independently labeled a predeclared critical issue, else 0 (still not legal/TNB approval).
- system: B0_DIRECT_VISION / B1_SIMPLE_RULES / H_HELIOPOLIS.
- prediction: FLAG, CLEAR, ABSTAIN, ERROR. CLEAR is only a bounded modeled check, never final due-diligence clearance.
- model_id: same model/version per paired case.
- latency_ms / api_calls / usd_cost: only actually observed values; leave empty when unknown.

Run against completed actual records:

    python benchmark_evidence.py --input PRIVATE_matched_results.csv --output PRIVATE_summary.json

The evaluator refuses missing methods, mismatched inputs/models, fake "real" ground truth, missing source metadata, invalid costs and duplicate case rows.

## How to interpret metrics

Report counts and denominators for true critical cases, false clearances (critical case predicted CLEAR), flagged critical issues, abstentions, errors, coverage, false flags on noncritical cases and counts of actually measured costs/timing. A system that abstains on all cases has no false clearances but zero automatic coverage; an abstention is NOT an accurate negative.

Separate DEVELOPMENT vs HOLDOUT and REAL vs SYNTHETIC. **Synthetic unit tests verify only the evaluator code and deterministic guardrails, never real-world Gemini extraction accuracy.**

## What is still missing before Issue #6 can be closed

1. Written permission for de-identified real land-title/SLD documents suitable for the cloud service selected.
2. Independent blinded expert labels: title restrictions and SLD symbols/wires.
3. A frozen holdout and a common model/version/prompt budget.
4. Actual executed B0/B1/H results, recorded latency, requests and cost, manual review decisions and errors.
5. Sufficient cases to support the conclusions; otherwise write **NOT ENOUGH EVIDENCE**.

Never upload identifiable owner records, invoices or electricity account details to a public repository. Obtain consent and handle private raw data in a compliant environment.
