# Public document references for Vertex AI OCR screening

**Scope:** Readable external document references, NOT redistributed source files and NOT a real-world accuracy benchmark. Updated 10 October 2026.

## 1. Malaysia: RISDA training slides with Perak title (Geran Mukim)

Official publicly viewable RISDA educational PDF:
https://kms.risda.gov.my/wp-content/uploads/2019/09/1466549455.pdf

- **PDF page 32 (1-based, zero-index 31):** First page of a Perak Geran Mukim. Visually contains title number 7202, Perak/Kuala Kangsar/Mukim Sayung, Lot 704, area 1.9728 hectares, land category Pertanian and Malay Reserve notation. Good first test of land-title page layout, area and restrictions.
- **PDF page 33 (1-based, zero-index 32):** Ownership entries with names, identity numbers and share fractions. **Contains personal data**; do not transmit to Vertex AI, copy to public GitHub, or republish without proper authorization, redaction and privacy review.
- **PDF pages 35–37:** Examples of Sarawak title pages. Different format/state; test as out-of-scope or needs manual review rather than forcing Peninsular Malaysian NLC fields.
- **Important:** The sample Perak first page is metric-only (1.9728 hectares), so the current parser's mandatory Ekar/Rood/Pole fields may flag review. That is a schema coverage problem, not necessarily an OCR failure. Also page 32 has no owner section, so a complete legal analysis must abstain.

## 2. Malaysia: TNB PV grid-interconnection technical guidebook

Publicly accessible copy of TNB design guidebook:
https://policy.asiapacificenergy.org/sites/default/files/TNB%20Technical%20Guidebook%20on%20Grid-interconnection%20of%20Photovoltaic%20Power%20Generation.pdf

SEDA's official download page (may require navigating its download UI):
https://www.seda.gov.my/pdfdownload/tnb-technical-guidebook-on-grid-interconnection-of-photovoltaic-power-generation/

- **PDF page 40 (zero-index 39):** Appendix A grid-connected PV system examples with/without storage.
- **PDF pages 41 and 42 (zero-index 40–41):** Appendix B PV **low-voltage** interconnection schematics, single-phase and three-phase.
- **PDF page 43 (zero-index 42):** Appendix C typical **11 kV interconnection feeder** protection and metering diagram.
- **PDF page 44 (zero-index 43):** Appendix D **33 kV** feeder.
- **Important:** These are instructional engineering figures, **not project as-built diagrams**, not proof of today's Solar ATAP approval, and not a complete example of every component the current Heliopolis SLD topology parser demands.

## Usage with Google Vertex AI

For a controlled **OCR extraction** trial, open the original PDF and export just the permitted figure/title page as a high-resolution PNG for your own Vertex AI environment. Make a handwritten field-level reference (e.g. title no., lot, hectares; PV symbols, wire connections) before examining model outputs.

Report **extraction accuracy separately from Heliopolis' preliminary rule verdict**. A correct extraction can still receive NEEDS_REVIEW because of missing owners, absent explicit anti-islanding relay, no separate transformer, or source jurisdiction. Never score an abstention as an OCR error without checking the source.

Do not upload full training-slide PDFs containing identity data as a shortcut. Public visibility is not a blanket grant of rights to transmit, republish or train on individuals' personal information.

For **real evidence of field generalization**, seek an authorized, de-identified complete title and independently annotated project SLD under your own permission. Only with those labels can Issue #6 and #7 be validated.
