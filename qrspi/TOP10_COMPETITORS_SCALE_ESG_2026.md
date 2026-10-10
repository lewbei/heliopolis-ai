# Heliopolis-AI — Top-10 Semifinal Positioning, Scaling and ESG Defence

Review date: 10 October 2026
Status: PROPOSED JUDGING MATERIAL. Do not merge/re-submit during a locked judging review window without written Organiser authorization.

## Executive verdict

A standalone proof-of-concept exists and the latest master GitHub Actions run was green with 186 offline Python tests. There is NO independent real-document OCR accuracy, live Vertex AI comparison, contractual solar/project savings, field engineering approval, revenue or deployed Cloud Run instance.

The credible product is NOT another end-to-end solar plant designer or regional GIS site-selection platform.

**Proposed beachhead: Malaysian solar-development evidence triage.** When a project analyst receives a Malaysian title, electrical SLD and basic project assumptions, Heliopolis can extract some fields through a Gemini model on Vertex AI, perform limited deterministic discrepancy/path checks and provide an explicit issue list with provenance and human-review gates.

The competitive claim is a PRODUCT HYPOTHESIS, not verified superiority or a proven unique capability. Existing enterprise competitors can be broader and more mature.

## MAIC official top-10 constraints

Official source: https://www.maicnexus.com/en/terms (terms v2.2, updated 19 September 2026)
And https://www.maicnexus.com/en/

- October semifinal: approximately 30 finalists compete for 10 Grand Final places, according to the published competition schedule.
- The public PRELIMINARY rubric, which may differ from semifinal instructions: Technical Feasibility 25%, Commercial Viability 25%, Industry Relevance 20%, Scalability 15%, ESG/National Impact 15%. Do not assert these are guaranteed final-stage weights.
- Repo/demo link must be publicly accessible during judging; broken or authentication-gated submitted artifacts can count as non-submissions.
- Submitted material is LOCKED during each notified judging review period and cannot be edited without prior organizer approval.
- Semifinalists must execute the Participation and Release Agreement before presenting or may be withdrawn.
- Do not alter T1 industry positioning. Core product must remain AI for clean-energy project development.

## Competitor map — where Heliopolis should NOT try to outclaim competitors

| Product/approach | Published capabilities | Heliopolis boundary / credible differentiation |
| --- | --- | --- |
| PVcase Prospect | Grid/parcel screening, ownership/zoning data, constraints, site feasibility, interconnection screening and layouts | Heliopolis focuses on PRE-ENGINEERING interpretation of incoming Malaysian title/SLD documents, not richer national parcel GIS, power flow or guaranteed better grid data. |
| Glint Solar | Large-area siting, constraints and environmental layers, layouts, site-control/landowner workflows | Complement with uploaded evidence reconciliation; do not claim Glint has no document support or that Heliopolis has production GIS capabilities. |
| Enverus RatedPower | Utility-scale PV/BESS layouts, detailed yield, electrical design, CAPEX and editable documentation | Heliopolis cannot compete as a bankable CAD/yield system. It proposes earlier document discrepancy triage before detailed engineering. |
| OpenSolar | Solar design, customer proposals, sales and project management | Different buyer and workflow: Heliopolis targets developer technical/legal dossier prechecks, not residential sales proposals. |
| Direct Vertex AI + ordinary checklist | Strongest low-cost baseline: same OCR model and a spreadsheet can already extract/check many fields | Only claim improvement if the full Heliopolis pipeline measurably lowers CRITICAL false clearances and/or analyst correction time at meaningful coverage. |

Sources:
- PVcase Prospect https://pvcase.com/de-risk-site-selection-solar-feasibility
- Glint Solar https://www.glintsolar.com/land-screening-eu
- RatedPower https://ratedpower.com/platform/
- OpenSolar https://www.opensolar.com/pro/

NO exhaustive competitive feature audit has been performed; do not claim worldwide-first or patented uniqueness.

## Why the layered workflow might matter

INPUT -> Google Vertex AI Gemini visual extraction -> field/geometry consistency checks -> Malaysian programme-specific *preliminary* rules -> review-required issue JSON.

Prototype-specific advantages that are IMPLEMENTED in some form:
- Synthetic demo and uploaded-document source types are labeled; an unreadable uploaded document cannot silently fall back to a passing synthetic title or SLD.
- Owner shares, areas and selected encumbrance fields are checked; majority share does not prove lease authority.
- LV electrical drawings do not automatically require an external transformer/relay; MV models a stricter relay/transformer path; a disconnected/bypassed modeled protection path is a review concern.
- 2026 Solar ATAP non-domestic energy-only monthly calculation is separate from LSS PPA and historical NOVA. No bankable ROI or automatic current scheme permission is issued.
- Auditable numeric screening and red flags are available as downloadable JSON.

But: field OCR may be inaccurate, land-title input schema still omits some metric-only/partial documents, visual wire connectivity may be misextracted, and strong competitors may have deeper integrations. This is an initial workflow claim awaiting evidence, NOT a demonstrated technical moat.

## Scaling: operational, geographic, and economic

Stage A: CURRENT prototype. One Python/Streamlit repo, optional Google Vertex Gemini for scanned images, deterministic Python/NetworkX checks and a separate Solar ATAP energy-only page. No deployed production multi-user tenancy, no Google Cloud Run deployment verified, and no e-Tanah/TNB private registry integration.

Stage B: PROPOSED private pilot. Deploy Streamlit or a small API in a controlled server environment (for example Cloud Run). Use an attached service account to Vertex AI, not API keys committed in .env; enforce user authentication, document-transfer permissions, storage expiry, audit logs excluding raw NRICs, job rate limits and per-case budget. The permission checkbox is not security/authentication by itself.

Stage C: PROPOSED repeatable paid workflow. Process independent project dossier jobs asynchronously; OCR once and cache only permissioned encrypted extracted fields; run deterministic checks without repeated model calls; offer assigned human review and versioned rule/scenario references. Scale infrastructure with number of dossiers, then independent customer accounts, not with fabricated count of synthetic sites.

Stage D: FUTURE geographic replication. Malaysian states have differing title/land rules. Each state needs source-versioned rules, licensed/local reviewer validation, authentic data permissions and test cases before activation. Other ASEAN markets are separate products requiring local legal and utility work; rules are not portable by changing country labels.

Mandatory pilot unit metrics:
- number of legitimate dossiers screened, percent critical evidence missing, false-clearance rate on independently annotated critical cases, abstention/coverage, analyst review minutes per pack;
- actual Vertex cost and latency per successful/failed file, storage/server cost, human correction minutes, and total cost per completed case;
- documented buyer willingness to pay/renew, rather than invented subscription revenue.

Financial value hypothesis: annual gross labour value = actual screened dossiers × measured review hours saved per dossier × buyer's own loaded hourly cost. Net value must subtract actual API, compute, compliance, reviewer and error-remediation costs. Do not publish a numerical ROI until these inputs are measured.

## ESG: measurable claims without greenwashing

Environmental (E):
- DIRECT CURRENT OUTCOME: Heliopolis creates review and constraint flags; the demo does NOT generate renewable electricity or avoid CO2.
- PROPOSED process KPI: percentage of candidate dossiers with verified environmental/land restriction flags before costly engineering, number of weak dossiers closed early, field work potentially avoided (only after a measured before/after comparison).
- FUTURE optional scenario: generation MWh × an appropriately selected counterfactual electricity GHG factor may support an indicative grid comparison for a CONFIRMED installed, generating plant. A software screening result is NOT evidence the plant was built, additional, or that Heliopolis caused the generation.
- CRUCIAL benchmark: Malaysia Energy Commission provisional 2024 grid emission factors published 23 February 2026: Peninsular 0.740, Sabah 0.539, Sarawak 0.199 tCO2e/MWh (numerically Gg/GWh). For 1,000 MWh, applying the PENINSULAR generation-average factor yields an illustrative *gross electricity-intensity equivalence* of 740 tCO2e. This is NOT verified avoided emissions, a causal impact of Heliopolis, a marginal emissions factor, or a carbon credit.
- Actual project impact should consider time/location-specific displaced generation, project additionality, embodied panels/construction emissions, habitat/land-use harms, REC ownership and double counting. GHG Protocol says avoided emissions should be disclosed separately from scope-inventory reductions.

Social (S):
- Prevent confidently wrong inferences about co-owner lease authority, charge/caveat implications or Malay Reserve, with mandated professional review. Potential benefit: earlier land-rights/consent visibility, not proven human-rights outcomes.
- Do not transmit personal titles/NRICs to Vertex AI without authorization. Use scoped consent, encryption, deletion, access controls and a PDPA review before public deployment. Never publicly expose raw documents in the repo.
- KPI: percent of reviewed cases retaining owner/consent exceptions and recorded human override, with zero unauthorized uploads targeted. These are aspirational targets until independently audited.

Governance (G):
- Source metadata, rule/model version, explicit NEEDS_REVIEW, reviewer identity, traceable finding basis and controlled escalation are the core governance value hypothesis.
- KPI: 100% of issued preliminary reports contain scheme, source/provenance, model and review flags (verify via automated tests and log sampling); zero unchecked automated approvals.
- Current JSON reporting provides some provenance; persistent audit, immutable storage, retention controls and access logs are FUTURE production work.

Official evidence:
- Malaysia Energy Commission provisional GEF https://myenergystats.st.gov.my/documents/d/guest/grid-emission-factor-gef-in-malaysia-2022-2024-provisional-
- GHG Protocol on separate project/avoided-emission disclosure https://ghgprotocol.org/blog/inventory-and-project-accounting
- Malaysia National Energy Transition Roadmap https://www.st.gov.my/resources/full-document-national-energy-transition-roadmap-energising-nation-powering-our-future

## Semifinal risk matrix, not a predicted competition score

- TECHNICAL — Demonstrable: 186 passing offline tests and failure-mode examples on master. Weakness: real Vertex image OCR and supported source formats have not been compared with expert labels.
- COMMERCIAL — Plausible buyer and workflow. Weakness: no measured correction time, paying customers, buyer interviews or cost/revenue evidence.
- INDUSTRY RELEVANCE — Malaysian solar development documents, grid/land/ATAP distinctions. Weakness: no developer-validated pain ranking or real project dossier.
- SCALABILITY — Stateless-ish deterministic rules and server-hostable Python are promising. Weakness: not deployed, per-file costs/security/concurrency not tested, state regulatory rules limited.
- ESG — Specific plausible process/GHG reporting pathways. Weakness: no independently measured emissions or social outcomes and no independent environmental GIS layers.

Top-10 shortlist viability is unknowable without other teams' scores and the organizer's semifinal rubric. Avoid percentage chance-of-winning claims.

## Three judge-kill tests to prepare BEFORE stage

1. LIVE INPUT + OCR: One authorized, de-identified genuine title and one LV drawing; record extraction of every visible field and missing-field abstentions. No proper comparison -> disclose NOT VERIFIED.
2. NEGATIVE CONTROL: Present a valid-looking synthetic title/SLD, then remove critical fields or bypass the LV protection path. Confirm NEEDS_REVIEW in both interface and downloaded JSON, without a fabricated approval.
3. PAYING BUYER: Explain exactly who uses one report, the next action it changes, cost per screening pack and a planned/actual test of willingness to pay. Do not assert saved weeks unless measured.

## Suggested aggressive judge questions and compact answers

Q: PVcase already does land and grid screening — what's new?
A: PVcase offers broader site/geospatial and design workflows. We test whether Malaysian title/SLD **incoming document triage** with explicit contradiction checks and human handoff adds value before detailed engineering. Not claiming a better PV design engine.

Q: Why not direct Gemini/Vertex + a spreadsheet?
A: It may be enough. Our B0/B1/H comparison is designed to test whether the extra graph and validation logic reduces critical false clearances or correction time beyond that cheap baseline. Today this incremental benefit is not measured.

Q: Does an LV connected diagram mean the system is TNB-approved?
A: No. It passes limited graph/label checks. Relay settings, inverter certifications, equipment tests and actual utility design decisions are external.

Q: How can this scale to 1,000 customers?
A: It has not been tested at that scale. The deployment proposal separates per-dossier server processing, account access, queue/rate limits, AI API quotas and expert escalations. An initial small pilot must measure real cost, latency and error rates first.

Q: How many tonnes of CO2 did your app avoid?
A: Zero VERIFIED avoided tonnes to date. We offer early screening, not generation. Any eventual project-impact calculation needs confirmed operating electricity, a counterfactual baseline, GHG Protocol separation and attribution evidence.

Q: Are you already working with Solarvest?
A: No signed partnership or pilot is claimed. We propose independent tests with interested developers; Solarvest is one potential stakeholder, not a software/data dependency.

Q: How accurate are the 186 passed tests?
A: 186 software tests passed; they do not measure OCR accuracy on naturally occurring legal/engineering documents.

## Requested actual deliverables, priority order

P0: Check official semifinal dashboard for review-window locking, signed participation agreement and public demo/repo access.
P0: One permitted real Vertex extraction with field-by-field QA and deterministic failure cases.
P0: A 4-minute demo recording accessible to judges, with synthetic/real labels, no private data and no dead links.
P1: Matched B0 direct Vertex vs B1 simple rules vs H Heliopolis on a small frozen set, report denominators and API cost. Even a negative result is evidence.
P1: One developer interview or letter confirming the priority pain (NOT a claim of adoption), and one measured manual-vs-tool review time.
P1: A one-page business model: buyer, pricing test and unit-cost formula. ESG KPIs should separate current measured process outcomes from future potential impact.

DO NOT add automated TNB filing, pretend registry access exists, add a second general LLM, or build a Southeast Asia policy engine before the minimal evidence gates above pass.


## Urgent reconciliation with prior prepared pitch artifacts

Previous saved presentation materials dated 7–8 October 2026 have been located, but we do not know whether they are the FINAL submission. They must not silently be replaced by a new nine-slide GitHub Markdown pitch:

- Heliopolis_AI_Competition_Pitch_20261007_v8.pdf is a 16-page pack (main narrative plus detailed Q&A). Its cover displays **13 October 2026** as the seminar date. Check the official dashboard/email, do not treat the cover as an event confirmation.
- Heliopolis_MAIC_Seven_Minute_Spoken_Script_20261008.pdf is a 7-minute script with a self-reported 8-minute cap, prepared for a **different 10-main-slide** narrative. Reconcile exact displayed deck and speech timing.
- That earlier working demo shows 3.21 MWac -> 2.00 MWac, both HOLD, with RM15.94m -> RM7.06m modeled CAPEX and RM4.608m storage removed under a prototype heuristic. **Current GitHub main uses BESS what-if OFF by default**, and statuses are PRELIMINARY_REVIEW_REQUIRED / NEEDS_REVIEW rather than the old HOLD state. Do not replay those historic numbers against new code or claim the CAPEX change comes solely from reducing capacity.
- The saved pitch/Q&A cites **232 Python/API checks plus 39 frontend checks** in an earlier local working environment. Current public master CI has **186 offline Python tests**, which is not an arithmetic or evidential contradiction if the suites differ, but each number must be attributed to its exact build and logs. Do not call either field OCR accuracy.
- The saved pitch proposes **RM3,000/year local installation licence**. Keep it as one SPECIFIC UNVALIDATED price hypothesis; clarify users/support/Google Vertex usage costs and buyer willingness to pay. Do not change the commercial offer among presentation, script and judge Q&A without explanation.
- The earlier speech explicitly avoids fresh live OCR and downloads during its 75-second demo. A new SLD negative-control tour or longer cloud demo needs a timed full rehearsal. If the existing 7-minute sequence is more reliable, preserve it and use the graph failure as a backup Q&A, NOT an untested on-stage substitution.

Top-10 priority on a short deadline: freeze ONE executable build, ONE matched slide deck, ONE spoken script, ONE saved reproducible result and ONE truthful test count. A stable five-to-seven-minute demonstration is worth more than adding new unvalidated features.

The proposed nine-slide draft is an ALTERNATE message framework only. It has not been substituted into the user's previous v8 pitch file and must not be merged into a possibly locked judging submission without explicit permission.
