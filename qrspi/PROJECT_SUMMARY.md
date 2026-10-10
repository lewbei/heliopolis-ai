# MAIC Nexus T1 — Heliopolis-AI Project Summary (PROPOSED UPDATE)

Status: draft for review, 10 October 2026. No edits to judging-locked submission materials without organizer permission.

## One-paragraph problem and product

Heliopolis-AI is an independently developed, AI-assisted **pre-investment solar document triage** prototype for Malaysian EPC and IPP project-development analysts. Optional Google Gemini visual extraction via Vertex AI processes PNG/JPG land-title and single-line diagram (SLD) images. Deterministic Python performs limited area/share validation, visible restriction flags, LV/MV modeled topology checks, synthetic terrain/yield screens and illustrative cash-flow or current Solar ATAP monthly energy-only calculations. The user receives labeled inputs, preliminary findings, and JSON reports with explicit human-review conditions. This is not land-title clearance, electrical approval, filing automation, GIS parcel search, or a bankable PV design.

## Differentiation that can be defended

Established suppliers already cover much of solar site selection, geospatial screening, plant design and CAPEX/yield analysis (PVcase Prospect, Glint Solar, RatedPower). Heliopolis does not claim global novelty or superior GIS/engineering. Its narrower proposal is a Malaysian title/SLD **incoming dossier-checking workflow** before engineers spend time on more detailed studies.

Direct Vertex AI plus a spreadsheet is the strongest simple baseline. The added value of owner-share checks, LV/MV graph logic, financial scheme boundaries, provenance and explicit abstention is a falsifiable hypothesis awaiting observed comparison, not a proven product moat.

## Actual implemented modules

1. Optional managed Google Vertex AI/Gemini OCR for uploaded images. Uploaded-document failures cannot silently switch to successful synthetic fixtures. No field-level extraction accuracy has been established.
2. Preliminary title analysis: area/unit and ownership fractions, recorded caveat/charge/Malay Reserve flags and review referrals. Not state-specific title compliance or legal lease authority.
3. Graph-based SLD: limited **LV** PV -> inverter -> optional AC switch/PV meter -> grid, with explicit drawn anti-islanding annotation or connected displayed relay; **MV** requires an external modeled relay/transformer path. No device certification, settings study or TNB approval.
4. Synthetic elevation/grading assumptions, MW/MVA grid-ratio sensitivity and illustrative LSS PPA yield/economics. No actual DEM survey or bankable project return.
5. Separate non-domestic Solar ATAP one-month energy-only page: billing import/export, Maximum Demand, allowable quantity, dated previous-month SMP, forfeiture and 10-year export-credit boundary. It is not a full TNB invoice, programme eligibility decision or long-term NPV.
6. A matched-evaluation **tool**, not an actual field benchmark, for B0 direct Gemini, B1 simple rules and Heliopolis; cannot claim real OCR accuracy from passing regression tests.

## Current evidence and what remains missing

Latest confirmed repository: 186/186 offline Python tests passing on master at the 10 October 2026 review; synthetic report and Streamlit smoke test green. Real Vertex AI field OCR labels, independent document baseline, buyer review minutes, paying customers and carbon outcomes NOT measured.

The built-in 500 Malaysian site examples and generated slope surfaces are SYNTHETIC. Uploaded real titles may contain personal information and should be handled only with authorization. PNG/JPG are supported; PDFs, metric-only/partial titles and production multi-tenancy still need broader input/schema work.

## Commercial/scalability hypothesis

First target: EPC/IPP technical or project-development analyst who repeatedly checks incoming land and electrical files. Potential chargeable value is measured review hours/critical mistakes averted per dossier; no price, savings, or contracted customers verified.

Technical scale is a staged plan: (a) current standalone Python/Streamlit demo; (b) secure limited cloud/Vertex pilot with a dedicated service account, authentication, no public PII, rate limits and real cost/latency records; (c) controlled repeatable dossier jobs and reviewer queue with versioned state-level scheme rules; (d) later geographic expansion only with independent local approvals and evidence. Cloud Run deployment is proposed, not completed.

## ESG and national relevance

Environment: possible earlier detection of unsuitable or environmentally constrained project sites, but no biodiversity GIS coverage or avoided CO2 has been measured. The current software does not generate electricity.

Social: flag possible co-owner / land restrictions and require human legal review rather than inferring blanket authority to lease. Privileged scans require explicit owner consent/security safeguards.

Governance: source-labeled fixtures and uploads, no fabricated pass on critical extraction failures and auditable preliminary findings. Enterprise audit, permissions and retention controls remain future work.

For any **future** modeled avoided-emissions discussion, use source-appropriate Malaysian Energy Commission grid factors with labelled year/region and disclose separately from GHG inventory per GHG Protocol. An illustrative MWh × average factor value is not attributable carbon savings by Heliopolis or a carbon credit.

## Requested small experiment

Seek an authorized 3–5-site exploratory pilot with independent title and electrical reviewers, freeze genuine inputs and labels, and compare direct Gemini, simple rules and Heliopolis on critical false clearances, abstention/coverage, reviewer minutes, cost and latency. Small n means only feasibility evidence and reported limitations, not broad generalization. For semifinal, provide a stable public synthetic demonstration and the live OCR test only if consent and actual credentials permit.

## Source links

Official MAIC terms: https://www.maicnexus.com/en/terms
Official Malaysian Solar ATAP: https://www.seda.gov.my/reportal/atap/
Competitor/scaling/ESG research (DRAFT branch): qrspi/TOP10_COMPETITORS_SCALE_ESG_2026.md
Pitch (DRAFT branch): PITCH_DECK.md
Code: https://github.com/lewbei/heliopolis-ai
