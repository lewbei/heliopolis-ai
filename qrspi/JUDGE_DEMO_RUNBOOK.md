# Heliopolis-AI — Semifinal 4–5 Minute Judge Demonstration (PROPOSED REVISION)

Updated 10 October 2026. A draft for review; no changes to locked judging artifacts without the organizers' permission.

**One primary product:** preliminary incoming-document checks for Malaysian solar EPC/IPP development analysts, NOT another bankable PV design tool.

**Timing:** This 4–5-minute sequence is an ALTERNATIVE. A 7-minute/10-slide spoken script dated 8 October also exists; use whichever matches the organizer's announced time limit and the exact deck/build rehearsed. Do not switch stories at the venue.

## Before the presentation

- Confirm the official semifinal Participation & Release Agreement and stage review-window dates. Official terms: https://www.maicnexus.com/en/terms
- Verify the EXACT submitted GitHub/repo/demo URL is publicly accessible to the judges. Private cloud OCR for confidential documents must stay behind authentication, not in a publicly exposed demo.
- Locally run: pip install -r requirements.txt ; then streamlit run app.py.
- Set the connection voltage class explicitly to MV for the default larger LSS demo. The default UNKNOWN cannot pass a scoped SLD topology screen.
- Have a pre-recorded offline synthetic demo if live connectivity fails. No private personal data or hidden API secrets in video.
- If presenting the older 3.21 to 2.00 MWac / HOLD case, first reproduce its output using that exact older implementation. Public master currently has BESS what-if OFF by default and uses NEEDS_REVIEW, not HOLD. The historical RM4.608m storage cost change was NOT solely due to smaller AC capacity.
- Do not mix old local 232 Python/API plus 39 frontend test counts with current GitHub master's 186 Python regression tests. Each is tied to different logs/builds and neither measures OCR accuracy.
- Use the latest PR/repository test result that you have ACTUALLY verified; at draft review 186 offline Python tests passed, not OCR accuracy.
- If organizer materials are LOCKED, do not replace submitted pitch materials until permission is granted.

## Timed demonstration (only what currently works)

| Time | Action | Judge takeaway |
| --- | --- | --- |
| 0:00–0:35 | Describe an EPC/IPP analyst receiving land title, electrical SLD and technical assumptions. | One buyer and one narrow pain, not generic AI-for-everything. |
| 0:35–1:05 | Select an explicitly SYNTHETIC LSS example, MV connection profile and illustrative LSS PPA sensitivity. | Source labels, no claim of government cadastral or actual grid data. |
| 1:05–1:45 | Open Electrical SLD Graph Audit; separate relay, transformer and grid connected. | Bounded preliminary modeled protection route, never TNB certification. |
| 1:45–2:15 | Toggle Connect Transformer to Grid OFF, keeping the drawn relay present. | NEEDS_REVIEW: present device does not prove continuous protected path. |
| 2:15–2:40 | In planning fields, download report JSON and verify grid_path_valid=false and the displayed source/assumptions. | Provenance and safe negative-control behavior. |
| 2:40–3:05 | Explain that corrupt uploaded scans or missing critical fields fail closed. Optional: set LV profile and show it needs visible inverter anti-islanding evidence even without external transformer. | Useful no-fabricated-clearance result; LV/MV profiles differ. |
| 3:05–3:35 | Contrast PVcase, Glint and RatedPower: stronger GIS/site/CAD; Heliopolis proposes Malaysian title/SLD dossier review before engineers. | Honest competitive wedge. |
| 3:35–4:05 | State 3-stage scaling hypothesis: current app, secure private Vertex pilot, account/rule-versioned repeatable dossiers. | Measurable scale, not imaginary nationwide integrations. |
| 4:05–4:30 | ESG: visible title restrictions/consent review and transparent assumptions; zero verified avoided CO2. Ask for 3–5 consented site pilot. | Impact measurement plan rather than greenwashing. |

## Alternative standalone Solar ATAP 30-second explanation

The separate **Solar ATAP Monthly** Streamlit page handles explicitly user-provided/synthetic non-domestic one-month import/export energy, MAQ and prior-month Average SMP, with no rollover. This is NOT the same buyer/scheme as a large utility LSS plant, not a full TNB bill, and not a bankable consumer ROI. Do not let this secondary feature dilute the main pitch.

## Optional real Vertex AI OCR, only with authorization

Use a permitted, anonymized actual title or TNB reference drawing and a configured Google Vertex AI project. The upload authorization checkbox allows transmission, but does NOT make public uploading of sensitive owner/NRIC records safe; proper tenancy/security review is separate. Field-by-field compare the Vertex output with original source; do NOT claim model success merely because JSON parsed. Corrupt or unreadable uploaded images MUST produce review/error, not synthetic data.

The repository's current OCR inputs are PNG/JPG (no general PDF page ingestion yet). Do not claim a complete metric-only/multi-page land-title extraction pipeline. The public RISDA/TNB reference sample sources are documented in PUBLIC_VERTEX_OCR_DOCUMENT_SOURCES.md, with privacy caveats.

## Harsh-judge Q&A

**Why not direct Gemini?** That may be sufficient. We have a matched B0/B1/H evaluator and need measured critical-error/reviewer-time evidence to justify extra logic. No false accuracy number is claimed.

**What does PVcase/Glint/ RatedPower already do?** Broad GIS/grid/site search, site design, yield and layout. We do not compete on that depth. We address upstream, uploaded Malaysian title/SLD dossier triage as an evidence-based pilot hypothesis.

**How does this generate money?** A project-development analyst would potentially pay to reduce measured dossier handling and error-remediation costs; no pricing, volume, time savings or paying customer is yet verified.

**What does an LV graph pass mean?** The modeled path and visible protection label pass bounded checks, not manufacturer's inverter certification, current utility settings or signed electrical approval.

**How will 100+ customers use it?** Cloud deployment, scoped Vertex service identity, per-user role control, temporary protected storage, independent review queues and measured cost/latency are a FUTURE plan; no production multi-user scaling has been tested.

**What is the ESG benefit?** Earlier possible red flags and record integrity are process benefits to measure. No real solar project has been developed or commissioned by this prototype, so no measurable direct avoided carbon can be attributed today.

**Does the 186-pass test prove OCR accuracy?** No. It proves only covered software behaviors under mocked/synthetic/offline conditions.

**Can Solarvest sign on today?** No established customer partnership or signed agreement. We want a small permissioned evaluation first; the tool is standalone from Solarvest systems.

## Final verification checklist

- [ ] Reviewer/Organizer authorizes any updates to submitted locked artifacts.
- [ ] Exact current submission link accessible without a password and without exposing real personal data.
- [ ] Test MV demo pass -> disconnect transformer -> NEEDS_REVIEW.
- [ ] Downloaded SLD status and UI status agree.
- [ ] If LV demonstrated, generic inverter without explicit anti-islanding evidence remains NEEDS_REVIEW.
- [ ] Demo clearly says SYNTHETIC when appropriate; live OCR is not pretended.
- [ ] Latest CI test count and PDF match current branch/commit.
- [ ] Provide a field evaluation gate and a concrete pilot ask, not a guaranteed Top-10/win claim.
