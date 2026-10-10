# Offline demo verification — 10 October 2026

## Source and scope

Source baseline: `lewbei/heliopolis-ai` master commit `8b2562a68be3d6e2a8b375d99b0462f28736b965`, rechecked unchanged after the tests. The 73 text/source/test files materialized for this audit matched their Git blob hashes before editing. Committed binary presentation/images were not materialized or modified. The runtime Python source was unchanged.

This change adds workflow regression coverage and reconciles stale README/runbook instructions. It does not change the user's designed presentation, introduce a model fix, deploy a service, or claim real-document validation. Issue #17's capacity/footprint correction already exists in the baseline and was verified rather than reimplemented.

## Checks performed

- Baseline: `python -m pytest -q tests` — **213 passed in 11.50s**.
- With the new workflow tests: `python -m pytest -q tests` — **216 passed in 14.27s**.
- Python compile check across runtime modules, pages and tests — passed.
- Local Streamlit startup health check — passed: `GET http://127.0.0.1:18501/_stcore/health` returned HTTP 200 with body `ok`; the process was then stopped cleanly. This establishes startup/health only, not browser rendering.
- `python solar_agent.py` and JSON assertions — passed; synthetic provenance, preliminary-review status, unverified transformer/voltage values, and illustrative LSS financial status preserved.
- Runtime used Python 3.12 in an isolated virtual environment with repository requirements; this does not reproduce the Dockerfile's Python 3.11 image build.

Three additional Streamlit AppTest workflows exercise:

1. The two-acre source preset, 3.21 → 2.00 MWac edit, current JSON AC/DC parity, unchanged parcel, withheld ROI, rerun determinism, and a fresh session reset.
2. An edited source's provenance, then switching presets without retaining original source hashes/case identity.
3. Repeated connected/disconnected MV graph toggles and exported topology parity; invalid capacity removes the previous downloadable assessment.

The tests run with `HELIOPOLIS_DEMO_ONLY=1`; both OCR entrypoints are replaced with failing mocks and asserted never called. The existing suite also checks that main-page image upload and Solar ATAP CSV upload widgets are absent in public-demo mode.

## Expected findings, not approvals

Both 3.21 and 2.00 MWac exceed the two-acre illustrative footprint screen (approximately 0.51 MWac). NPV/IRR remain withheld. The original auxiliary sensing/control relay requires electrical review. Current calculations are not a reproduction of historical slide cost bars or optional-storage assumptions.

## Explicitly unverified

Browser screenshot/visual QA was **blocked**: Chromium failed at `socket()` with `EPERM`, including after a scoped elevated execution attempt was admitted. No browser screenshot, successful browser launch, or visual sign-off is claimed. Streamlit AppTest validation does not replace a real-browser rehearsal. A separate same-process local server check returned HTTP 200/`ok`; browser rendering remains unverified.

No live Vertex calls, real document transmission, deployment, wallet action, Docker image build, authenticated customer workflow, engineering validation, legal clearance, or field accuracy benchmark was performed. Dependency versions remain unpinned in the repository, so future fresh installs need a rerun of the suite.

## Reproduce

From the repository root with the requirements installed:

    python -m compileall -q solar_agent.py heliopolis_ocr.py app_logic.py app.py solar_atap_settlement.py atap_profile_io.py benchmark_evidence.py pages tests
    python -m pytest -q tests
    python solar_agent.py

For an operator's subsequent browser rehearsal:

    HELIOPOLIS_DEMO_ONLY=1 streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false

Follow the current-code sequence in `JUDGE_DEMO_RUNBOOK.md`; manually verify the health endpoint and complete an actual browser rehearsal before treating the UI as visually approved.
