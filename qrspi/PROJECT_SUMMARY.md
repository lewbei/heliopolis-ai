# Heliopolis-AI — MAIC T1 Project Summary (Draft)

**Track:** T1 — AI for Clean Energy
**Product:** Malaysian solar-project document triage
**Status:** Preliminary prototype; not a legal, grid or financial approval
**Submission:** Draft only; do not replace locked materials without organiser permission.

## Problem

Solar EPC and independent power producer (IPP) analysts reconcile Malaysian land titles, electrical single-line diagrams (SLDs) and early cost assumptions before paying for detailed engineering. Missed restrictions, inconsistent ownership shares, ambiguous connections or incorrect subsidy/programme assumptions create review risk. We have not measured the prevalence or cost of these errors.

## Solution and innovation

Heliopolis-AI offers one structured, source-labelled preliminary issue report. An optional Google Gemini model accessed via **Vertex AI** extracts visible fields and electrical diagram symbols/wires from authorized uploaded PNG/JPG scans. Python then screens owner-share totals, area consistency, selected title restrictions, modelled LV/MV connection paths and illustrative project assumptions. Missing or contradictory critical evidence produces **NEEDS_REVIEW**; it never becomes simulated approval.

The innovation hypothesis is **combining Malaysian title and SLD evidence into an auditable early review workflow**, not inventing a new OCR model. Existing site-selection and PV design platforms are more mature in GIS, layout and engineering. Our closest low-cost competitors are direct Vertex extraction and a normal analyst checklist; any performance advantage remains unproved.

## Working evidence

The public GitHub repository contains a Streamlit prototype, synthetic demonstration inputs, downloadable preliminary JSON, and **186 passing offline Python tests** on the verified master build. The LV SLD screen recognizes a modelled PV–inverter–grid path without requiring a separate external transformer; anti-islanding evidence still requires expert confirmation. A distinct Solar ATAP page performs one-month energy-only calculations, **not** a complete utility bill or bankable return.

Synthetic fixtures and software test passes do **not** demonstrate accuracy on independently labelled real documents. There are no confirmed paid customers, utility approvals or verified staff-hour savings.

## Buyer and commercialization

Initial target: Malaysian EPC/IPP project-development analysts handling repeat document reviews. The existing commercial hypothesis is a **RM3,000/year local licence**, subject to testing of buyer interest, seats, support and Vertex/compute costs. Planned scaling is controlled secure deployment, per-dossier processing, professional review queues and versioned state-specific rules—not automated government filing or already operational multi-tenancy.

## ESG and validation

**Environmental:** investigate earlier detection of unsuitable/restricted sites and avoided unnecessary studies; no attributable CO2 reduction has been demonstrated. **Social:** surface landowner and consent concerns for qualified legal review and protect personal data. **Governance:** preserve source provenance, assumptions and unresolved exceptions.

**Ask:** an authorized **3–5-site exploratory pilot** with independent land/electrical reviewers. Compare direct Vertex AI, a simple checklist and Heliopolis using the same inputs, recording false clearances, coverage, correction minutes, per-file cost and buyer willingness to pay. Advance deployment only if the incremental value is measured.

**Repository:** https://github.com/lewbei/heliopolis-ai
