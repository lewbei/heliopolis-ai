# Heliopolis-AI — MAIC Semi-Final Runbook for Latest Nine-Page Pitch

**Authoritative narrative:** user-supplied nine-page visual PDF, \`Heliopolis_AI_MAIC_20261008_Main_Pitch (2)(1).pdf\`, uploaded 10 October. Original SHA-256: \`d70a11a9a7c0f6a9fb0cd9b15d9e46f2b225e2b172608cac7c11e3c4ad40620d\`.

This replaces the ALTERNATE nine-section narrative previously in PR #16. This document is supplementary to the **source-faithful [seven-minute rehearsal script](TOP10_REHEARSAL_SCRIPT_7MIN_DRAFT.md)**. It does not overwrite the user's original designed slide PDF. Confirm exact date/duration and submission lock with organisers: https://www.maicnexus.com/en/faq.

## Original deck order (nine images; no change to their message)

1. Cover — Solar project screening for Malaysian teams.
2. Prepared Perak example — fictional title and SLD, project figures.
3. Gemini extraction → reviewed inputs → code checks → one report.
4. The saved 3.21 → 2.00 MWac case; **HOLD FOR EXPERT REVIEW** remains.
5. Saved illustrative costs: **RM15.94m → RM7.06m** upfront, **−RM9.79m → −RM2.66m** discounted value. **RM4.608m** of the change is attributed to a *prototype storage assumption*, not only capacity.
6. Existing software and Malaysian consultancy services. Proposed Heliopolis RM3,000/year, not proven buyer willingness to pay.
7. Malaysian solar developer/consultancy buyer; proposed local licence and matched current-workflow comparison.
8. Land counsel, electrical reviewer and site survey; proposed process-impact measures, environmental outcomes unmeasured.
9. One traceable preliminary report; thank you, Wudibei Lab.

**Never** replace this user-provided main story with the older PR's nine-section alternative, especially its emphasis on a new live LV-protection demonstration in slide 4.

## Preflight

- [ ] Verify the competition portal's exact uploaded PDF and assigned slot. Slide cover says 13 October 2026, but the caption alone is not official scheduling evidence.
- [ ] Confirm organiser's slide-size/review-lock requirements. The original uploaded file is 5.72 MB; a visually verified nine-page compressed version of 2.21 MB was prepared and provided back to the user. The repo's Matplotlib-generated \`pitch_deck.pdf\` is **only a text derivative**, not the user's original slide design until that PDF is manually replaced.
- [ ] If demoing the old **HOLD** report, load the **same old application build/data** used to generate those saved screenshots. The current GitHub \`master\` uses \`NEEDS_REVIEW\` and optional BESS off by default. Do NOT claim old cash-flow/Storage results were freshly reproduced by current code.
- [ ] If old matching app is unavailable, use the prepared screenshots (slides 4–5) and explain explicitly that they are a saved illustrative case.
- [ ] Confirm any repo/demo link is accessible as submitted. Never commit \`.env\`, credential JSON, real owner identifiers or confidential title images.
- [ ] Have an offline screenshot fallback. Optional permissioned Vertex OCR must be rehearsed separately and measured field by field.

## Current GitHub master — OPTIONAL Q&A-only negative-control example

1. Start \`streamlit run app.py\` on the exact verified code commit.
2. Select a synthetic representative site and choose an explicit **MV** voltage profile in the sidebar.
3. Open Electrical SLD Graph Audit; show modeled relay/transformer connected path.
4. Disable **Connect Transformer to Grid**, leaving relay present. \`NEEDS_REVIEW\` should appear; this is a graph failure, NOT an engineering certification decision.
5. Verify that the exported JSON graph status matches the displayed result.
6. Label this as a **different current-code demo**; do not substitute the graph for the user's slide-4 historical HOLD screenshot or attach the 3.21/2.00 financial numbers to it without reproducing identical old assumptions.

## Hostile-judge short answers

**Why not direct Vertex AI?** Vertex provides the candidate visual extraction. Heliopolis adds deterministic share, modeled connection and scenario checks. The incremental accuracy/reviewer-time advantage has not been measured on real held-out examples. The cheapest meaningful baseline is Vertex plus a checklist.

**What is actually different from PVcase, Glint, RatedPower or local solar consultants?** The hypothesis is one Malaysian incoming dossier report combining title, SLD and early assumptions. Existing competitors have deeper GIS/site, PV design or consultancy capabilities. Do not claim to be the first or only one.

**Is HOLD an approval or a legal conclusion?** No. Saved scenario shows questions for title counsel and power-systems review. An independent specialist must clear material decisions.

**Do the capital-cost bars imply RM8.88m savings?** No. The charts are illustrative, and RM4.608m of the difference comes from the specific prototype storage assumption. Do not attribute the entire change to smaller PV capacity.

**Does an SLD path prove TNB compliance?** No. Certification, relay settings, external protection requirements and actual drawn connectivity still require qualified review.

**Are three saved synthetic OCR calls an accuracy benchmark?** No. Current repo has offline tests, but independent OCR accuracy and developer time savings remain unmeasured.

**What's the commercial offer?** Proposed RM3,000/year local licence to produce accepted-input/review reports. Customers, scope and willingness to pay have not been validated.

**How will this scale?** Today it is standalone Python/Streamlit; controlled cloud deployment, access/security, reviewer workflows and region-specific rules are proposed pilot stages, not current multi-user production proof.

**What is ESG impact?** Earlier review transparency and possible reduced duplicated work are proposed to measure; no verified carbon savings or attributed new solar generation yet.

## Version / evidence compatibility

The user's nine-page latest visual PDF is NOT the October 7 v8 16-page presentation nor the prior repository's alternate nine-section draft. Use one single source of truth for the on-stage slide order. Older local 232 Python/API + 39 frontend checks and current public master 186 offline tests are separate environments; neither is a field-OCR accuracy rate.

**Do not quietly alter the user's 9-page visual PDF.** The source image, layout and text remain authoritative; the GitHub markdown and any auto-rendered simple PDF are just readable derivatives.
