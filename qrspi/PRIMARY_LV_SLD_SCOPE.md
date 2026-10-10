# Primary low-voltage SLD screening (TNB Appendix B)

**Scope:** Implemented as an additional LV *drawing topology* profile, not grid-connection approval. Existing MV demonstration remains separate and strict.

## TNB reference (inspect pages, do not redistribute its figures)

- Official SEDA / TNB technical guidebook: https://www.seda.gov.my/pdfdownload/tnb-technical-guidebook-on-grid-interconnection-of-photovoltaic-power-generation/
- **Appendix B, printed page 41 (PDF index 40):** Single-phase LV PV drawing. PV DC strings feed an inverter, AC switches and a PV meter, then the LV L/N/E connection. No mandatory externally drawn relay or dedicated step-up transformer in that diagram.
- **Appendix B, printed page 42 (PDF index 41):** Three-phase LV equivalent.
- Guidebook **section 6.6**: anti-islanding inverter functionality matters and must be proven in pre-commissioning. See **section 6.20** for islanding protection.

This is an engineering **reference diagram**, not a licensed drawing of an operating customer's plant, verified Vertex AI OCR accuracy or evidence of 2026 TNB acceptance. Confirm current scheme and grid code with qualified professionals.

## Explicit profile semantics

- **LV:** A modeled PV → inverter → grid connection is the primary topology. Intermediate AC_Switch and PV_Meter nodes are permitted. There is no *universal requirement* for an external relay or transformer symbol on the LV drawing.
- **Displayed anti-islanding evidence:** An explicitly printed anti-islanding/non-islanding or IEC 62116 label associated with an inverter must be extracted as a boolean *true* and an exact short source text. Alternatively, a separately modeled and connected anti-islanding relay is accepted as **drawing evidence only**. Generic inverter icons or model assumptions cannot prove it.
- **LV possible outcome:** PRELIMINARY_TOPOLOGY_PASS only when every modeled PV has a grid path through the inverter and a displayed protection element, with no bypass. The result NEVER means certified inverter equipment, correct settings, correct switching, commissioning tests or TNB compliance.
- **LV missing label:** NEEDS_REVIEW with the note that anti-islanding evidence is not visible. This is NOT the same as declaring a generic LV diagram invalid for omitting a separate MV relay or step-up transformer.
- **MV:** Existing PV → inverter → external relay → transformer → grid preliminary screen remains strict and unchanged.
- **UNKNOWN or HV:** This limited prototype has no adequate drawing profile and returns NEEDS_REVIEW, not a fraudulent positive screen.

## How to demonstrate offline

1. Run from repo root: streamlit run app.py
2. In sidebar, select **Connection voltage class = LV** (user assumption).
3. Open **Electrical SLD Graph Audit**, leave synthetic inverter anti-islanding annotation visible and inverter connected to grid. See the bounded preliminary LV route.
4. Disable **Explicit inverter anti-islanding label shown**. Result must change to NEEDS_REVIEW (equipment/certification evidence missing).
5. Re-enable label; disable **Connect inverter to grid**. Result must change to NEEDS_REVIEW (broken circuit).
6. Try UNKNOWN or HV input, or an uploaded image without authorization, and confirm no positive screen.
7. If a permitted TNB reference image is extracted through Vertex AI, check original symbol/wire labels manually. The reference LV diagram does NOT label anti-islanding certification explicitly, so an OCR graph that extracts its shown devices correctly may still result in NEEDS_REVIEW. This is *correct abstention*, not proof of extraction failure.

## Evidence/provenance limits

The extracted bool/source text is unverified OCR, not a signed manufacturer datasheet. The LV check does not yet verify every AC switch, PV meter, grid reference, junction or grounding element because the current graph categories only capture a bounded subset. Reliable engineering approval needs current utility procedures, detailed design, device type test documents and expert review.

The new tests are **synthetic negative controls** for topology and metadata; they do not constitute field OCR accuracy.
