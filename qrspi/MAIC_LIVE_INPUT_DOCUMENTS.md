# MAIC 8 October 2026 — Exact Synthetic Inputs for Live Demo

**Source:** The original user-authored \`Heliopolis_AI_MAIC_20261008_Main_Pitch.pptx\`, slide 2. The latest nine-page PDF shows these images, but GitHub previously did NOT contain their standalone PNG source files.

**Prepared download:** In this ChatGPT conversation, \`Heliopolis_MAIC_Live_Demo_Inputs.zip\` contains the EXACT extracted PNGs, a two-page printable PDF, manually checked reference fields, and older saved app/terrain screenshots. The binary assets are not yet part of the GitHub repository. To recreate them deterministically from the original PowerPoint, run the hash-checked extractor:

    python scripts/extract_maic_demo_inputs.py /path/to/Heliopolis_AI_MAIC_20261008_Main_Pitch.pptx --output demo_inputs

The original PPTX is essential. Do not run the extractor on a different version; it refuses mismatching hashes. No Vertex OCR request is needed for recovery.

## Actual original input 1 — synthetic title

- File: \`01_SYNTHETIC_Perak_Land_Title.png\`, original 1800 x 2200 pixels; SHA-256 \`8e3178cd01a4cf09a3b7ce017a0131f9368057f37e1b29c8638f601ea546f694\`.
- Title SYNTH-GRN-2026-001; lot SYNTH-LOT-001; Perak; Synthetic District; Synthetic Mukim; Bangunan.
- **Land area = 2 Ekar, 0 Rood, 0 Pole**. Caveat recorded **YES**; charges NO; Malay Reserve designation NO.
- Owners: SYNTHETIC PERSON ALPHA / SYNTH-ID-0001 / 60/120 and SYNTHETIC PERSON BETA / SYNTH-ID-0002 / 60/120.
- This is a training image, not a government title or valid ownership/lease authority. The caveat makes legal review necessary.

## Actual original input 2 — MV single-line diagram

- File: \`02_SYNTHETIC_MV_SLD_Auxiliary_Relay.png\`, original 1800 x 1050 pixels; SHA-256 \`005f7bad7133e41c4fce758c73682486b6a4f5fc5365de76b62eae01d55f9246\`.
- The figure labels its Point of Connection **11 kV MV** (synthetic).
- Main route: PV ARRAY → INVERTER → TRANSFORMER → GRID CONNECTION.
- **The anti-islanding relay is connected to a separate sensing/control branch. It is NOT in series on the main electrical path.** The slide explicitly says protection operation is not assessed. This is NOT proof of TNB compliance.
- In the current MV topology screen, a failure to establish the required modeled protected path should give **NEEDS_REVIEW**, not a false electrical clearance. Check actual Vertex extracted symbols/wires against the original drawing.

## Demonstration A: safe 75-second OFFLINE graph negative control

    pip install -r requirements.txt
    streamlit run app.py

1. Open local Streamlit; select a clearly synthetic **Perak standard preset**, financial scenario **LSS PPA**, and explicit **MV** connection profile.
2. Go to **Electrical SLD Graph Audit**. Synthetic relay and transformer-connected controls ON → limited preliminary path.
3. Switch **Connect Transformer to Grid** OFF (relay still drawn) → **NEEDS_REVIEW**. Show that the displayed finding and exported SLD JSON agree.
4. This offline synthetic app fixture is NOT the identical 2-acre title/auxiliary-branch SLD recovered from the slide! The current Perak form preset includes **over 12 acres**, while the recovered slide title contains **2 acres**.

No Google credentials or live extraction are used on this path. It is a regression demonstration, not source-document OCR.

## Demonstration B: true live Vertex AI extraction of the two recovered PNGs

1. Configure an authorized Google Cloud Vertex AI project, model, IAM identity and Application Default Credentials locally/privately. Never commit \`.env\` or service-account credentials.
2. In the running Streamlit main app, under **Scanned Document OCR**, upload the two recovered **PNG images**, choose **MV** connection profile and authorize transfer to the configured Google model.
3. Inspect **actual** extraction outputs and compare them field-by-field against the labeled source images. The image itself is synthetic and does not raise real-owner data concerns, but Vertex transmission still needs approval.
4. Expect review conditions: the synthetic land title reports a caveat, and the picture's relay is on an auxiliary branch. Do not promise a green TNB result.
5. In case of malformed OCR fields, a failed model request or incompatible SLD wire extraction, show **NEEDS_REVIEW** rather than quietly substituting a successful test fixture. A live Vertex OCR result has **NOT yet been independently verified** in this project.

## CRITICAL demo mismatch: saved HOLD-cost slides vs current public app

The latest source pitch, Slides 4–5, displays an EARLIER saved demo: 3.21 → 2.00 MWac, both **HOLD**, costs RM15.94m → RM7.06m, negative NPV values, and a RM4.608m change due to the older storage-assumption rule. The current \`master\` app uses **NEEDS_REVIEW** and hypothetical BESS OFF by default.

More seriously, the current \`YieldFeasibilityEngine.calculate()\` uses **land area** to estimate DC capacity, gross yield and CAPEX, instead of taking the sidebar's \`Proposed AC Capacity (MWac)\`. Merely adjusting 3.21 → 2.00 MWac does NOT reproduce the saved financial chart. The source title's **2 acres** also should not be confused with the current 12+ acre form preset. See [blocking live capacity comparison issue](https://github.com/lewbei/heliopolis-ai/issues/17).

**Recommendation for actual slides 4–5:** present the ORIGINAL saved screenshots as historical, illustrative prepared results. For a currently executable live Q&A use the separate, clearly labeled offline SLD negative-control demonstration. Do not claim the older HOLD/cost scenario ran live on current \`master\`.

## Stage preflight

- Nine-slide user PDF is the authoritative presentation, not the repository's text-backup PDF.
- Pre-open the Streamlit localhost in a browser; GitHub Pages alone cannot host Python/Vertex. There is **no confirmed public live app URL** from the repository.
- Keep this source ZIP available offline on the laptop, not only via a chat download link.
- Verify exact pre-rehearsed controls, screenshot fallback and any actual Vertex API credentials before entering the presentation room.
- Do not re-upload confidential Malaysian title records, owner IDs or API keys.

**Scope:** This document and the recovered media are faithful to the user's synthetic slides; no new real Malaysian dataset was created.
