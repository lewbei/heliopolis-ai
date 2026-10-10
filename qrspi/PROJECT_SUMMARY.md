# MAIC Nexus 2026 — Heliopolis-AI Project Summary

**Track:** T1 — AI for Clean Energy  
**Prototype:** https://github.com/lewbei/heliopolis-ai  
**Review date:** 10 October 2026

## One-paragraph description

Heliopolis-AI is a prototype **AI-assisted preliminary solar-site screening** system designed for Malaysian project-development analysts. It uses Gemini Vision to extract structured fields from uploaded land titles and electrical single-line diagrams; deterministic Python then performs unit conversions, ownership-share arithmetic, constrained SLD topology checks, illustrative terrain/energy calculations, and financial sensitivities. The outputs flag items needing professional review. **It is not a land-title clearance, TNB grid-code certification, Solar ATAP eligibility decision, SEDA submission or bankable investment recommendation.**

## Industry problem and approach

Solar developers routinely reconcile heterogeneous land, electrical and financial records. Our **hypothesis** is that earlier automated extraction and transparent checks can reduce avoidable errors and manual screening effort. We have **not measured** generalizable savings or field OCR accuracy. The prototype demonstrates a testable method rather than claiming complete due-diligence automation.

## Actual AI and deterministic components

1. **Gemini Vision OCR:** optional cloud-based perception for title fields, electrical symbols, wires and junctions. Missing or unreadable uploaded evidence must return a review/error status and must never be substituted by pre-approved synthetic data.
2. **Legal screening:** interprets area units and share fractions and flags selected visible restrictions; shares alone do not determine property execution authority. Title records require solicitor/land-office verification.
3. **SLD graph screen:** a NetworkX graph tests modeled PV -> inverter -> anti-islanding relay -> transformer -> grid paths, including bypass/disconnection flags. Results are preliminary; no protection-setting or full utility compliance model exists.
4. **Civil/financial sensitivity:** synthetic terrain examples, offline representative solar-resource inputs and simplified CAPEX, OPEX, yield and NPV/IRR assumptions. No actual topographic survey or financial bankability is claimed.
5. **Regulatory planning fields:** model selected published NEM NOVA LV/MV CAS study-fee bands separately from LSS economic scenarios; never state the inferred amount is an approved quotation. A simplified AC MW/MVA screen does not establish an obligatory BESS requirement.

## Important programme boundaries

**Solar ATAP is not a complete supported modelling scenario.** Official non-domestic limits include inverter output <= 1 MW and <= 100% of consumer maximum demand; the export offset arrangement lasts 10 years. Our multi-MW demonstration must not be marketed as ATAP-eligible. Consumption/export profiles, accurate energy tariff elements and current programme rules require separate evaluation.

Official references:
- https://www.seda.gov.my/reportal/atap/solar-atap-guidelines/
- https://www.seda.gov.my/reportal/atap/solaratap-general/
- https://www.seda.gov.my/reportal/nem/

## Demonstration and evidence

Run `streamlit run app.py` (requires Python dependencies). Built-in site registry and generated slope surfaces are **synthetic** demonstration material. Uploaded-title and uploaded-SLD paths use Gemini and fail closed when evidence is incomplete; offline regression tests intentionally exercise those failures. See GitHub Actions for current compile/test results rather than assuming passing tests demonstrate real-world accuracy.

For the semifinal demonstration, show: (a) an explicitly synthetic site screening, (b) a faulty SLD flagged for review, and (c) an unreadable uploaded document producing an error instead of a fake clearance.

## Customer value and proposed pilot

Potential customers: solar EPCs, IPPs and their project-development analysts. The proposed B2B product is a source-traceable preliminary screening workflow, with expert verification retained for high-stakes decisions. We are **seeking**, not claiming to have secured, a 3–5 site pilot. Its measurable outcomes should include field extraction correctness, false-clearance rate, manual correction effort, processing time, abstention frequency, and utility/legal reviewer acceptance. Compare matched documents against direct Gemini extraction plus conventional deterministic spreadsheet/checklist baselines.

## Current limitations

- Synthetic samples are not an accuracy benchmark.
- Land records and grid schematics have not received independent legal or TNB validation.
- No verified Solar ATAP offset economics, live land-office integration, automatic filing or customer contract.
- Production data security and permissions require an additional deployment review.

**MAIC presentation:** [PITCH_DECK.md](../PITCH_DECK.md)  
**Source and implementation:** [README.md](../README.md), `solar_agent.py`, `app.py`, `heliopolis_ocr.py` and `tests/`.
