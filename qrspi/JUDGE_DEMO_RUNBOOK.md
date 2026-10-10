# Heliopolis-AI — MAIC T1 Semifinal Demonstration Runbook

**Duration target:** 4–5 minutes demo + Q&A.  
**Product claim:** AI-assisted *preliminary* solar-site screening, not final engineering or legal clearance.  
**Pitch PDF:** [pitch_deck.pdf](../pitch_deck.pdf) (generated from [PITCH_DECK.md](../PITCH_DECK.md)).

## Before going on stage

Run `pip install -r requirements.txt` and `streamlit run app.py`. Open the local URL. Keep a terminal with `pytest -q tests` ready if the judges request reproducibility.

Use the built-in preset/demo mode. The site registry, owner names, terrain and financial parameters are **synthetic/illustrative**, not verified documents or real project deals.

Do not rely on live Gemini credentials for the fallback presentation. Run a separate live upload demonstration **only if** it has already been tested with valid credentials and permissible example documents.

## Demonstration sequence

| Time | Action | What judges should see |
| --- | --- | --- |
| 0:00–0:35 | State the problem and narrow product claim. | Preliminary screening, not approval. |
| 0:35–1:15 | In the sidebar, select a synthetic site and LSS PPA scenario. | Clearly labeled synthetic inputs and illustrative calculations. |
| 1:15–2:15 | Open **Electrical SLD Graph Audit** with both synthetic toggles on. | A modeled protected path; result says **PRELIMINARY**, not TNB-approved. |
| 2:15–2:45 | Turn **Connect Transformer to Grid** off, leaving relay present. | `NEEDS_REVIEW` for the broken circuit. |
| 2:45–3:10 | Open the **SEDA/TNB Planning** tab and download JSON. | The exported `sld_topology_screen` matches the currently shown failure. |
| 3:10–3:35 | Reset the circuit; explain that an uploaded unreadable document stops with a downloadable review report. | No fabricated compliance after extraction failure. |
| 3:35–4:30 | Explain commercial hypothesis, intended pilot and key known limitations. | Demonstrated logic vs unvalidated impact are separated. |

### Optional live OCR exercise (not a required proof)

Use a non-sensitive title/SLD that you have the right to upload, with an already-tested Gemini API key. If the model cannot extract critical title fields or diagram geometry, let the app display `NEEDS_REVIEW`; do **not** swap into a synthetic fixture and call it successful OCR.

An uploaded document is one cloud OCR invocation per assessment render; Streamlit reruns on widget changes and may make further calls. SLD fixture toggles are disabled in uploaded-SLD mode. Review privacy/retention requirements before using genuine title deeds.

## What **not** to claim

- No verified OCR accuracy on independent Malaysian real titles/SLDs or demonstrated customer savings.
- No SEDA/TNB authorization, electrical protection setting verification, or land-office clearance.
- The >15% AC-MW/MVA metric is a **heuristic**, not a TNB battery requirement.
- Solar ATAP is **not** a completed economic model; multi-MW demo sites are not eligible by simply selecting a C&I scenario.
- An illustrative positive NPV does not establish investment viability.
- Do not imply Solarvest is an existing customer or commercial partner.

## Likely skeptical questions

**What does the AI actually do?** Gemini Vision extracts fields and diagram geometry. The legal-share arithmetic, graph checks, and cash-flow calculation use deterministic Python. No custom trained solar foundation model is claimed.

**Why not a spreadsheet and a generic OCR prompt?** That is a valid baseline. The proposed pilot compares Gemini-only extraction and spreadsheet checklists with the full pipeline using identical documents and review budgets.

**How safe is a green result?** It is a bounded preliminary result, not a safety certificate. The system fails closed on OCR errors and flags selected structural inconsistencies; real protections and ownership constraints need expert review.

**What about the 51% co-owner rule?** Ownership fractions do not establish power to lease a whole parcel. The software marks legal coordination for professional review.

**How do you know it saves time?** We do not yet. The first 3–5-site pilot would measure review effort and false-clearance rates.

**Is your 500-site dataset real?** No: synthetic scenarios to demonstrate the interface. We will not present them as field-validation results.

## Verification checklist

- [ ] Open app successfully in offline preset mode.
- [ ] Visible SLD changes to `NEEDS_REVIEW` when the transformer path is disconnected.
- [ ] Downloaded JSON reports `grid_path_valid: false` in that state.
- [ ] Error uploads do not silently produce a successful synthetic analysis.
- [ ] Latest GitHub Actions Python tests and PDF rendering jobs are green.
- [ ] Present [the generated PDF](../pitch_deck.pdf), **not** a stale copy stored on a different device.
