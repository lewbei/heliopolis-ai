# Heliopolis-AI — MAIC Nexus T1 Semifinal Pitch (PROPOSED REVISION)

**Positioning:** Independent Malaysian solar-project **pre-investment document triage**: land-title and electrical-drawing extraction, limited deterministic consistency screens and explicit human-review handoff. Not automated permits or bankable feasibility.

**Repository:** https://github.com/lewbei/heliopolis-ai
**Demo:** streamlit run app.py
**Evidence status:** Synthetic fixtures and 186 offline regression tests; real Vertex OCR field accuracy, buyer savings, customer adoption and ESG outcomes remain unverified.
**Submission caution:** Draft only. Do NOT amend a locked MAIC review submission without prior Organiser authorization.

---

## Slide 1 — Opening

### A promising solar project can fail before engineering even begins.

A Malaysian project analyst receives a land title, an electrical single-line diagram and uncertain site assumptions. One unreadable restriction or misconnected protection path can change the next decision.

**Our wedge:** Heliopolis-AI turns incoming project documents into a structured PRELIMINARY issue review, not an approval or a new solar plant design tool.

---

## Slide 2 — The document bottleneck

### The user is an EPC or IPP project-development analyst.

Problem: Title areas and co-owner shares disagree; an electrical SLD omits or disconnects equipment; historic and current solar programme rates are confused.

Existing GIS and PV design tools do much more sophisticated engineering. Our narrower question is: **Can these incoming documents be screened consistently before paying for full legal and engineering review?**

**Hypothesis only:** fewer critical mistakes and less reconciliation work. Real savings require a matched pilot.

---

## Slide 3 — Exactly what AI and Python do

1. INPUT: uploaded title/SLD image or clearly synthetic demo; user-entered project assumptions. Cloud transfer requires authorization.
2. VERTEX AI GEMINI: extract visible title fields, symbols and wire geometry. We have not trained our own OCR model.
3. DETERMINISTIC VALIDATORS: area/share/restriction checks, LV/MV drawing-path checks, qualified grid and financial sensitivities.
4. OUTPUT: source-labelled issue and assumption report, human-review flag and JSON export.

Corrupt or incomplete uploaded evidence must not fall back to a passing synthetic project. Extracted labels are still unverified until a human compares them with the source.

---

## Slide 4 — Three reproducible demo outcomes

1. SYNTHETIC LSS project: show title fields, assumed MV connection, selected PPA sensitivity and connected PV -> inverter -> relay -> transformer -> grid graph.
2. NEGATIVE CONTROL: disconnect the MV transformer-to-grid line with the relay still present. Expected output: NEEDS_REVIEW; a present device is not a connected protection path.
3. FAILED uploaded image: malformed or missing critical fields fail closed and offer a review report, not a fake connected circuit.

**Show:** the displayed graph's verdict and the downloaded JSON must agree. Do not imply an actual TNB drawing has been validated by Vertex in this offline run.

---

## Slide 5 — Difference from existing solar software

**PVcase Prospect / Glint Solar:** strong site, parcel, grid and environmental screening. We do not claim better GIS or substation capacity data.

**RatedPower:** deeper PV layout, energy yield, CAPEX and electrical design. Heliopolis is NOT a competing bankable engineering design engine.

**OpenSolar:** installation design, proposals and sales workflows. Our primary buyer is the upstream dossier-review analyst.

**Direct Vertex AI plus checklist:** our hardest baseline. The unproven added value is whether specific graph and consistency checks reduce critical false clearances at useful reviewer coverage. Benchmark this rather than claiming to be world's first.

---

## Slide 6 — Technical and regulatory boundaries

LAND: owner-share arithmetic is not lease authority. Caveats, charges and Malay Reserve need professional/local review.

SLD: LV can show PV -> inverter -> switch/meter -> grid without a separate drawn relay/transformer; drawn anti-islanding evidence still needs verification. MV uses a stricter modeled path. Neither is grid approval.

LSS: illustrative PPA yield and NPV, not a signed contract or surveyed terrain.

SOLAR ATAP 2026: a SEPARATE non-domestic one-month energy-only page models MAQ, prior-month SMP and credit forfeiture. It is not a complete TNB bill, eligibility certification or 21-year ROI.

---

## Slide 7 — Evidence: what passed and what has not

**Implemented:** functioning Streamlit/Python prototype, source-labelled synthetic examples, negative controls, separate consumer monthly screen. Latest confirmed master run: 186/186 offline Python tests, synthetic-report checks and Streamlit smoke.

**Not yet demonstrated:** representative real Vertex OCR accuracy; matched B0 direct AI / B1 simple rules / H Heliopolis advantage; measured analyst minutes, actual API cost, customer adoption or independent utility/legal outcomes.

**Next kill test:** a few permitted, independently annotated real titles and LV diagrams. Report false-clearance rate, abstention/coverage, correction time and cost. A negative result is still an honest result.

---

## Slide 8 — Who pays, and how it scales

**Initial buyer:** small/mid-sized Malaysian EPC or IPP project-development analyst reviewing incoming document packs. Start as a reviewer-assist tool, not a permit-filing robot.

**Value hypothesis:** measured packs per month x corrected analyst hours per pack, minus actual Vertex, compute, storage and human-review costs. Pricing and time savings have NOT been validated.

**Scale plan:** current offline prototype -> controlled cloud pilot with Vertex service identity, restricted documents and per-file limits -> versioned state/scheme checks and independent customer accounts. No live e-Tanah integration, production multi-tenancy or cross-border compliance is claimed today.

---

## Slide 9 — ESG, safeguards, and the ask

**E:** pilot metric = expert-confirmed unsuitable land/restriction flags detected before paid engineering. Actual carbon avoidance is UNMEASURED; screening alone produces no electricity.

**S:** surface co-owner/land rights and restriction flags for professional review. Require document-upload authorization and protect personal identifiers.

**G:** pilot metric = complete source/review labels in every report and no false approval; data transfer consent, rule versions and overrides remain explicit.

**ASK:** One consented 3–5-site pilot with independent engineering/legal reviewers, one interested development analyst and a matched baseline. Measure false clearances, coverage, correction time, unit cost and willingness to pay BEFORE expansion.

**Closing:** Make solar due-diligence mistakes visible earlier. Do not pretend engineers or land offices have been replaced.

---

## Harsh-judge quick answers

**Q: Other companies already screen solar sites. What is different?** We target Malaysian incoming title/SLD document review before detailed engineering, not a superior GIS, CAD or bankable yield engine. Incremental value still needs comparative measurement.

**Q: Why not use Vertex AI with a spreadsheet?** That is our B0/B1 comparison; the graph and consistency layer must earn its cost by reducing critical wrong clearances and reviewer effort.

**Q: Why call this AI?** Vertex AI Gemini performs optional multimodal OCR. Python performs the deterministic screening. We do not own or retrain the foundation model.

**Q: Does a green LV path establish TNB compliance?** No. It means a limited modeled connectivity/visible-label check passed. Inverter certification, settings, metering and commissioning are not checked.

**Q: Are the 500 sites a real Malaysian database?** No. They are explicitly SYNTHETIC scenarios and cannot be used as field-accuracy evidence.

**Q: Your code passed 186 tests; what is real OCR accuracy?** Not established. Offline unit/regression tests cannot establish real-world Vertex extraction performance or time savings.

**Q: How many paying clients or saved analyst hours?** No confirmed paying clients or measured time savings yet. The proposed pilot is to determine those values.

**Q: How many tonnes of CO2 has your software saved?** Zero VERIFIED or attributable avoided tonnes so far. ESG process outcomes will be measured separately from actual installed solar generation and the relevant emissions counterfactual.

**Q: Can this run on GitHub Pages without a server?** No; Streamlit and Vertex use Python and require a server. A proposed Cloud Run deployment is not currently claimed to be live.

**Q: What about state-specific laws and sensitive documents?** Each Malaysian state/scheme needs evidence-based, versioned rules and expert review. No private titles are publicly posted and real data transfer needs authorization.

**Q: What will make you commercially viable?** Measured case volumes, lower error-adjusted review cost and willingness to pay. If Heliopolis adds no value over a direct Vertex plus checklist baseline, narrow or stop the concept.

### References for technical judging (not evidence of Heliopolis performance)

- https://www.maicnexus.com/en/terms
- https://pvcase.com/de-risk-site-selection-solar-feasibility
- https://www.glintsolar.com/land-screening-eu
- https://ratedpower.com/platform/
- https://www.opensolar.com/pro/
- https://www.seda.gov.my/reportal/atap/
- https://myenergystats.st.gov.my/documents/d/guest/grid-emission-factor-gef-in-malaysia-2022-2024-provisional-
- https://ghgprotocol.org/blog/inventory-and-project-accounting
- https://github.com/lewbei/heliopolis-ai/blob/master/qrspi/TOP10_COMPETITORS_SCALE_ESG_2026.md
