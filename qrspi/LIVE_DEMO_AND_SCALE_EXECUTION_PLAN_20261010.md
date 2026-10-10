# Heliopolis-AI — Live MAIC Demo + Scalable Delivery: Execution Plan

**Plan created:** 10 October 2026, Asia/Kuala_Lumpur.
**Target event:** latest user-uploaded nine-page deck says 13 October 2026. Confirm the actual stage slot and duration with the organiser.
**Source of truth:** the user's latest 8 October nine-page pitch, not the GitHub markdown-text backup PDF. The source title and SLD PNGs were recovered and supplied as Heliopolis_MAIC_Live_Demo_Inputs.zip in ChatGPT. Media hashes and field expectations: [MAIC_LIVE_INPUT_DOCUMENTS.md](MAIC_LIVE_INPUT_DOCUMENTS.md).
**Baseline at plan time:** GitHub master commit 3f86709a, 191 offline tests passed; no Cloud Run service URL or live Vertex field-level QA verified.
**Status:** actionable plan, NOT an assertion that the work below has been implemented.

## Product and service boundaries

One core product: **preliminary Malaysian solar-project dossier review** (incoming title + single-line diagram + project assumptions -> accepted fields, deterministic issues, human handoff, auditable report). Google Gemini through Vertex AI provides optional visual extraction; Python provides unit/fraction, graph and financial arithmetic. Never present title clearance, TNB compliance, project suitability or bankable ROI.

Keep the separate non-domestic Solar ATAP monthly energy-only calculator clearly labeled a supporting consumer workflow. It must not affect the LSS proof story or inherit LSS tariff/eligibility assumptions.

**Source-grounded demo inputs, NOT interchangeable:**

| Input | Actual source | Expected behavior |
| --- | --- | --- |
| Synthetic title PNG, 2 acres, caveat, two owners 60/120 each | User's original slide 2 | Correct field extraction candidate and NEEDS_LEGAL_REVIEW, not a cleared project |
| Synthetic 11 kV SLD PNG | User's original slide 2 | PV-inverter-transformer-grid power route; auxiliary sensing/control anti-islanding relay (not an inline relay) must NOT be falsely called a certified protection path |
| GitHub Perak form preset, >12 acres | Separate demo fixture | Must be labeled independent synthetic fixture, never the recovered 2-acre land title |
| Saved 3.21 -> 2.00 MWac, HOLD, cost bars RM15.94m -> RM7.06m | Historical presentation build | Archive-only illustrative screenshot until its exact model/assumptions are reproduced; current master uses NEEDS_REVIEW and BESS off by default |

## Critical blockers before the stage (implement in this order)

### P0-A: Consistent project inputs and finance — GitHub #17

Current `app_logic.compute_assessment()` sends Proposed AC Capacity to grid ratio/manifest but `YieldFeasibilityEngine.calculate()` estimates PV DC capacity and CAPEX solely from parcel area. Thus changing 3.21 to 2.00 does not honestly replay the slide's cashflow. The title in the source pitch contains **2 acres**; current Perak preset contains **>12 acres**.

Minimal repair:
1. Define one immutable ProjectCase record: case_id, provenance, title area, proposed_ac_mw, ac_dc_ratio (explicit assumption; prior demo ratio 0.85), slope/weather source, scenario, optional storage, user-selected LV/MV, and source-hashes.
2. Refactor the financial engine to accept the selected AC rating and derive DC rating using documented AC/DC assumption. Compute modeled footprint limit separately from plant size; do not silently swap the title's area with a demo parcel.
3. Using existing illustrative density: max DC MWp = area_m2 * 0.9 / 12140; max AC MWac = max DC MWp * 0.85. A **2-acre** lot screens at about **0.51 MWac**, so **3.21 or 2.00 MWac must be flagged as footprint-implausible**. This is a heuristic, not a substitute for a PV plant layout/survey.
4. When proposed capacity exceeds area screen, flag NEEDS_REVIEW and withhold any claim of an eligible/bankable project. Optional user-selected hypothetical financial sensitivity can still be shown but must be marked incompatible with the recovered parcel.
5. Keep slide 5's historical HOLD/cost numbers as archive examples until the older inputs/calculator are independently reproduced. Do NOT force current code to reproduce old storage CAPEX by manipulating assumptions.

Proof required: changing a valid case's AC MW changes estimated DC capacity, yield, CAPEX and cashflow; changing only the title area changes max-land rating; title 2 acres + 3.21 MWac returns NEEDS_REVIEW; JSON and visible values always match; older archived values never masquerade as fresh results.

### P0-B: One-click source-corrected synthetic review

Add a "Prepared MAIC 2026 case" selector, not manual re-entry of ten sidebar fields. It must load a checked, versioned fixture with the original title/SLD hashes, title=2 acres and owners/caveat, MV profile, and the reviewer status. Separate "View original document" from "Use current demo fixture" explicitly.

Use original recovered PNGs after verifying rights and private content. Do not ship actual identity data or pretend a fictitious title is authentic. Show 3 simple outcomes:
- connected synthetic MV circuit -> topology-only preliminary path (fixture specifically contains inline modeled relay, explicitly not the original auxiliary-branch image);
- original auxiliary-branch SLD -> main power route detectable but protection-operation NOT VERIFIED -> NEEDS_REVIEW;
- disconnect inverter/transformer / remove a critical field -> NEEDS_REVIEW, no switch to another input source.

UI should always show: Case ID, SYNTHETIC/EXTRACTED_UNVERIFIED, filename + hash, modeled voltage class, current expected status, all missing/unknown flags, and "not TNB/legal approval".

### P0-C: Live Vertex AI proof without stage risk

Do NOT presume the code's configured model is available to your exact GCP project/region: first run one tiny authenticated model request with the configured model and record returned model/region/latency. The existing `heliopolis_ocr.py` uses the Google Gen AI SDK and selects Vertex mode from GOOGLE_CLOUD_PROJECT. Enable the appropriate API/billing and obtain permitted authentication; never commit service-account JSON, GOOGLE_APPLICATION_CREDENTIALS or .env files.

Preflight only the two recovered synthetic images:
- Title expected fields: SYNTH-GRN-2026-001, SYNTH-LOT-001, Perak, Bangunan, 2 acres, caveat YES, charges NO, reserve NO, two owners 60/120.
- SLD expected: PV, inverter, transformer, grid + separate auxiliary relay; **distinguish power wires from sensing/control**. Misreading the relay as a connected inline device must be a review finding.
- One invocation per image per input hash + model version. Explicit "Re-run OCR" only after a user action; Streamlit widget rerenders must NOT silently bill twice.
- Save date/model/version, input SHA, raw response in a *protected local location*, parsed fields, error classification, review corrections and actual cost/latency. The on-stage response must be a PUBLIC SAFE SUMMARY without names/NRICs. The original media is synthetic.
- Run once independently, manually verify the JSON against the images. If extraction is partial, show that honest NEEDS_REVIEW outcome; this is still a useful working fail-safe.
- Freeze a labeled **RECORDED VERTEX RESULT** with actual model, date and source SHA as the no-network fallback. Do not label recorded output LIVE.

Stage requirement: stage demonstration MUST run without Vertex connectivity; live OCR is optional bonus, never necessary to finish.

### P0-D: Public judge URL + protected OCR environment

**Choose Google Cloud Run for Python/Streamlit**. GitHub Pages cannot execute the Python backend.

Deployment A (PUBLIC, synthetic only):
- One container hosting `streamlit run app.py` using Cloud Run's assigned `PORT` and `0.0.0.0` binding.
- `HELIOPOLIS_DEMO_ONLY=1` (NEW, must be implemented with SERVER-SIDE enforcement): hide/reject all user file uploads and paid Vertex requests, expose only preapproved synthetic demo cases, no private GCP data or credentials. Public service identity has **no Vertex AI permissions**.
- Limit max Cloud Run instances initially to 1–2, requests/concurrency modestly, set startup/health check, max upload and request limits as appropriate; log technical errors without personal data.
- Public URL can be loaded anonymously in a new incognito browser and a phone on another network.
- When possible deploy from a pinned tested Git commit; never update it hours before judging.

Deployment B (PRIVATE, Vertex):
- Separate Cloud Run service/revision or controlled local environment, access through Google Cloud IAP/organization identity. The current app's "I authorize upload" checkbox is NOT authentication.
- Dedicated user-managed service account with ONLY the necessary Vertex AI permission, and required relevant Cloud Run permissions. Cloud Run service identity supplies ADC; never set a service-account JSON path on Cloud Run.
- User authorization, filename/hash checks, file-size caps, model/region check, quotas, timeout/retry limits, private deletion policy, and no public raw document URL.
- Stage use is optional. If public judge access is required, show only safe synthetic/recorded outputs and optionally use an authenticated operator demonstration locally.

Suggested launch is two Cloud Run service names `heliopolis-demo` and `heliopolis-review`. No need for React, database or microservices before 13 October.

### P0-E: Freeze exactly one speaking/demo story

The user's nine-page visual deck is THE stage artifact; do not replace it with the repo's text renderer. Sequence is cover -> actual synthetic documents -> OCR/review layers -> saved 3.21/2.00 HOLD comparison -> storage caveat -> competitor map -> proposed RM3,000/year local licence -> measured ESG-process hypothesis -> final ask.

Keep Slides 4–5 marked historical/saved and explain their BESS/area caveat. If a current capacity-adjustment live demo is absolutely needed, first repair P0-A, use a separate correctly sized parcel fixture, and state those are **current recalculated values**, not the historic slide's RM figures.

For a 7-minute rehearsal, allocate:
- 0:00–1:15: problem + exact input title/SLD (slides 1–2)
- 1:15–2:05: extraction, reviewed inputs, validation/output (slide 3)
- 2:05–3:20: stage demo with proven synthetic graph negative case, then archived comparative HOLD example with disclaimer (slides 4–5)
- 3:20–4:25: alternatives, targeted buyer and **proposed** RM3,000/year price (slides 6–7)
- 4:25–5:35: scaling, real data safeguards and ESG with no unverified carbon claim (slide 8 discussion)
- 5:35–6:20: next pilot on 3–5 authorized cases, comparison with direct Vertex plus spreadsheet, measurable false-clearance, correction minutes and cost
- 6:20–7:00: closing and remaining stage buffer (slide 9)

There is an older seven-minute source script in ChatGPT, but its screen cues refer to the historic HOLD interface. Rehearse with the actual selected build, not both interfaces.

## Chronological tasks up to intended 13 October stage

| When | Essential task | Exit criterion |
| --- | --- | --- |
| 10 Oct evening | Freeze exact nine-slide PDF, source ZIP, stage objective and P0 #17 acceptance tests | One approved document/input list and no ambiguous site/source mixing |
| 11 Oct, first work block | Fix area-versus-AC finance coupling, explicit mismatch HOLD/NEEDS_REVIEW, and JSON parity | New deterministic tests pass, on-screen re-run uses actual capacity |
| 11 Oct, second block | Recover/display exact synthetic PNGs, create selected case, test true sensing-branch SLD | Expected title fields and review status appear without fake clearance |
| 11 Oct / 12 Oct | One real authorized Vertex AI test, save sanitized run log and reproducible recorded result | Actual model/region works or clearly marked unavailable; no secret leak |
| 12 Oct | Package Streamlit to Cloud Run with explicit PUBLIC DEMO ONLY mode and private OCR separated | Public URL/anonymous refresh works, no cloud OCR possible on public mode |
| 12 Oct, evening | Run complete negative-control and format/privacy tests; freeze pinned Git SHA and save screenshots/video | CI green; 2 rehearsals under actual organizer time limit |
| 13 Oct, before slot | Warm app, test URL via phone/mobile, disable untested cloud features, keep local offline fallback | Presentation passes without WiFi, Vertex, or browser download reliance |

These are planning targets rather than promises of completion. If time runs out, CUT optional live Vertex, Solar ATAP, PDF upload support and multiuser features first. Do NOT cut a reliable offline screen/failure demonstration, provenance or the stage fallback.

## Definition of DONE for the live demo

1. Latest pitch PDF opens (9 slides); stage laptop has optimized original offline, not the repo-generated text derivative.
2. Exact source ZIP has two expected synthetic PNGs and verified SHA hashes; no real NRIC.
3. Demo starts on localhost; preferably a Cloud Run public synthetic URL also opens in an incognito session.
4. No external credentials/API needed for the main 75-second failure demonstration.
5. Synthetic connected MV path is explicitly labeled preliminary; disconnecting changes verdict to NEEDS_REVIEW; **report JSON equals UI**.
6. Original source title's 2 acres and caveat are visible; area-incompatible 3.21/2.00 proposals are flagged rather than misrepresented as feasible.
7. If operator runs private Vertex, real OCR response and field mismatches are recorded honestly. If unavailable, use ACTUAL labeled recorded output.
8. Every synthetic/assumed/Vertex-extracted value is identified. No confident TNB/legal approval, fake carbon savings, paid customer or ROI claim.
9. Application can be restarted and reloaded with no stale result from a previous case; malformed images fail closed.
10. A separate judge opens the exact submitted link, uses the demo and exports a report without your help; failures are documented and resolved.

## Scalable product architecture AFTER the stage

Use the SAME validated checking code rather than rewrite it.

Phase 1 (0–30 days after stage): private, single-tenant paid-beta architecture:
- Authenticated cloud front end; Google IAP or controlled identity.
- Post each dossier as one job: files -> private encrypted Google Cloud Storage -> queued processing (Cloud Tasks or equivalent) -> Vertex visual extraction -> schema/graph/finance rules -> reviewer decision -> versioned preliminary report.
- Use a private metadata store only when persistent user jobs are needed; immutable case IDs, source hashes, rule/model versions, original evidence references, retries and report revisions.
- Basic security: file limits, AV/content validation, retention and deletion, no raw NRICs in logs, minimum IAM, quotas, per-file budget, explicit consent and audit trail.

Phase 2 (30–60 days): 3–5-site pilot and matched benchmark:
- Permissioned (and, when possible, de-identified) real title/SLD documents; independent manual gold labels.
- B0 direct Vertex vs B1 Vertex + simple checklist vs H Heliopolis, on the SAME documents/model budget.
- Measure **critical false clearances, decision coverage, abstentions, field match, correction minutes, latency, actual Vertex token costs and all-in reviewer cost**. No n=3 claim of broad statistical accuracy.
- Test buyer's RM3,000/year local licence hypothesis; ask which seat/support/Vertex charges are included.

Phase 3 (60–90+ days): measured multi-tenant scale:
- Isolate tenant storage/identities; per-account quotas, rate limits, staff permissions, export restrictions, retention.
- Async worker scaling by number of documents; token and model usage tracked per job, error queues and immutable review history.
- Autoscale ONLY after collecting p50/p95 processing time, memory, API quota failures, human reviewer throughput and cost/10/100/1,000 dossiers.
- Malaysian state-specific title requirements and utility-programme rules are **versioned rules**, each needing independent specialist review and regression cases. Regional ASEAN support is NOT a drop-in configuration.

## Cost, ESG and reliability accounting

Cost per completed dossier = (actual Vertex OCR calls + Cloud Run compute + storage/egress + human checking + retries/failures + ongoing support). Annual buyer value = observed number of dossiers × measured review hours saved × loaded staff cost − all-in annual product cost. Compare against the cheapest viable Vertex+spreadsheet baseline.

Cloud cost guards: per-user request caps and model budget, a small Cloud Run maximum instance setting, billing alerts and, where applicable, service-specific enforced spend caps. Budget controls are **not** an exact universal hard ceiling and can incur delayed overage.

ESG: primary realistic CURRENT feature is governance (source traceability + explicit review) and social safeguard flags (owner/consent restrictions). Environmental KPIs are pilot hypotheses: verified potentially unsuitable sites surfaced before paid detailed studies, repeat study/site trips actually avoided. No proven CO2 reduction is attributable to this software today. Any future solar electricity-to-CO2 comparison needs real commissioning/generation and appropriate counterfactual accounting.

## Exact engineering work items / proposed code changes

- `solar_agent.py`: capacity-driven sizing, footprint plausibility, separate human-review flags; extend electrical power/control edge categories only as necessary.
- `app_logic.py`: one ProjectCase input contract; propagate real selected AC MW to every consumer; preserve per-source file and fixture identifiers.
- `app.py`: prepared-case picker, clear preliminary status, force demo-only restrictions server-side, manual rerun button for OCR; show stale/changed values correctly.
- `heliopolis_ocr.py`: verified model/region with explicit error details sanitized; source-linked fields, caching by image hash/model, bounded retries; never fabricate SLD wire or title identities.
- `tests/`: capacity-change, 2-acre vs 3.21/2.00 negative controls, auxiliary-control-branch SLD, title-share/caveat, API failure/timeout, privacy and CSV/report parity, Cloud Run startup/public-mode restrictions.
- `Dockerfile`, `.dockerignore`, optional `.streamlit/config.toml` and `scripts/deploy_demo.sh`: reproducible build and pinned deployment.
- `qrspi/MAIC_LIVE_INPUT_DOCUMENTS.md`: source-hashed input truth; `qrspi/JUDGE_DEMO_RUNBOOK.md`: exactly rehearsed approved stage story.

## Official operations documentation

- Cloud Run Streamlit quickstart: https://docs.cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-streamlit-service
- Cloud Run service identities / ADC: https://docs.cloud.google.com/run/docs/securing/service-identity
- Cloud Run IAP: https://docs.cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run
- Cloud Run instance cap: https://docs.cloud.google.com/run/docs/configuring/max-instances
- Gen AI SDK: https://googleapis.github.io/python-genai/
- Cloud billing budgets/caps and limitations: https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps

**DO NOT** push .env or GCP service-account JSON to GitHub, commit confidential or unreleased land records, submit a different pitch without checking the organizer portal's review lock, or treat software-unit-test pass percentages as OCR accuracy.
