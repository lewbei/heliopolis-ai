# Heliopolis-AI — MAIC Nexus T1 Semifinal Pitch

**Positioning:** AI-assisted **preliminary** solar-project screening in Malaysia. Not a legal opinion, professional electrical design, grid approval, or bankable financial recommendation.

**Repository:** https://github.com/lewbei/heliopolis-ai  
**Demo:** `streamlit run app.py`  
**Evidence status:** Synthetic/illustrative fixtures and unit tests are available; independent field-validation accuracy, customer adoption and time savings have **not** been established.

---

## Slide 1 — Opening

### A solar site can look promising until the documents disagree.

Project teams reconcile land titles, protection diagrams, land conditions and financial assumptions before making expensive engineering decisions. Heliopolis-AI combines AI document extraction with deterministic checks to flag **issues requiring human review earlier**.

**One-line product:** "Preliminary solar-site screening with traceable calculations and explicit uncertainty."

---

## Slide 2 — The user's problem

Solar project-development analysts receive different file types, inconsistent fields and site assumptions. A wrong land area, overlooked encumbrance, omitted protection relay or unsuitable financing scheme can change an early screening decision.

**Pilot hypothesis — not a validated fact:** structured extraction plus auditable checks can reduce manual reconciliation and help identify problems earlier. Time saved and false-clearance rates must be measured on real, permitted project documents.

---

## Slide 3 — System architecture

```text
Uploaded land title / electrical SLD
                |
        Gemini Vision extraction
                |
  Schema checks + missing-field detection
                |
  +-------------+-------------------+
  |             |                   |
Title/share   SLD graph        Terrain + finance
arithmetic    connectivity      assumptions
  |             |                   |
  +-------------+-------------------+
                |
      PRELIMINARY SCREENING
       - findings and caveats
       - source/fixture provenance
       - needs-human-review conditions
```

**AI's exact role:** multimodal perception. **Python's role:** unit conversions, ownership share sums, topology traversal, yield/cash-flow arithmetic. No trained Heliopolis foundation model is claimed.

---

## Slide 4 — Product demonstration: three outcomes

1. **Clearly labeled synthetic scenario:** show the input, selected finance scenario, numerical outputs, SLD topology and review notes.
2. **Faulty SLD:** a present-but-disconnected protection relay must yield `NEEDS_REVIEW` rather than a confident grid-compliance claim.
3. **Failed extraction:** missing Gemini credentials, unreadable legal restrictions or malformed SLD geometry must **stop** the uploaded-document assessment, not silently produce a compliant demo fixture.

The demonstration is **not** a live Malaysian land-office or TNB integration.

---

## Slide 5 — Engineering scope and limits

- **Land:** preliminary field and owner-share consistency; no claim that 51% share automatically authorizes lease execution.
- **SLD:** check modeled PV -> inverter -> anti-islanding relay -> transformer -> grid connectivity. A graph pass is **not** a TNB approval, relay-settings study or electrical certification.
- **Terrain:** generated elevation profiles are synthetic, not surveyed or lidar-derived project terrain.
- **Finance:** CAPEX, loss factors, PPA/offset rates, WACC and yield assumptions are scenario inputs, not bankable quotes.
- **BESS/grid:** simple AC-MW / upstream-MVA ratio is a sensitivity screen, not a load-flow study or mandatory 15% battery trigger.

---

## Slide 6 — Regulations matter: do not mix schemes

**LSS PPA:** standalone utility-scale economic sensitivity, subject to applicable procurement and connection requirements.

**NEM NOVA / illustrative C&I offset:** separate earlier scheme; current eligibility and export credit must be verified independently. Rate assumptions are not customer-specific electricity-bill calculations.

**Solar ATAP (2026):** **not implemented** as a complete eligibility/financial model. The published non-domestic rule caps inverter output at **1 MW** and **100% of consumer maximum demand**; export-credit arrangement is **10 years**, followed by self-consumption without export offsets. Do **not** present the example ~5.9 MWac system as Solar ATAP eligible. Actual offsets require load/export profiles and verified tariff components.

**Authorities:** 
- https://www.seda.gov.my/reportal/atap/solaratap-general/
- https://www.seda.gov.my/reportal/atap/solar-atap-guidelines/
- https://www.seda.gov.my/reportal/nem/

---

## Slide 7 — Evidence, not inflated benchmarks

What exists: an executable Python/Streamlit prototype, unit/integration tests and reproducible synthetic fixtures. The repo's CI runs tests and performs Python compilation.

What is **not** yet demonstrated: field OCR accuracy on held-out legal records, SLD error rates on real drawings, time savings against a manual process, utility validation, Solarvest partnership, or revenue.

**Next empirical pilot:** 3–5 consented real projects, blinded expert labels, comparison with direct Gemini extraction and ordinary spreadsheet checks, measurement of correction time, false-clearance rate, abstention, accuracy and latency. Do not score "needs review" as a verified negative.

---

## Slide 8 — Customer and commercial validation

Potential users: solar EPC project developers, IPPs and due-diligence analysts.

**Starting integration:** project-development analyst uploads title/SLD and enters proposed technical assumptions, receives a preliminary issue report before engaging a surveyor, conveyancing lawyer and power-systems engineer.

**Proposed business model (unvalidated):** enterprise screening/workflow subscription or integration. Test willingness to pay and time saved during a pilot. Do not claim signed customer contracts.

---

## Slide 9 — Final ask

We seek an industry pilot partner to validate the accuracy and decision value of preliminary screening on 3–5 real Malaysian solar projects. The pilot will define measurable go/no-go criteria before adding registry integration or automatic application drafting.

**Closing:** "Heliopolis-AI does not replace the engineers. It makes early assumptions visible, repeatable and reviewable."

---

## Harsh-judge quick answers

**Q: What is AI here?** Gemini Vision extracts unstructured fields and diagram geometry; deterministic code checks those outputs. We do not call fixed calculations "AI inference".

**Q: Can it legally approve a title?** No. It reports preliminary flags. Owner shares cannot prove legal authority to lease an entire lot.

**Q: Does a green electrical graph mean TNB compliance?** No. It means only that the modeled drawing passes specific path checks; protection settings, utility studies, and approvals remain external.

**Q: How accurate is real OCR?** Not enough evidence yet. Unit-test success does not quantify production document accuracy.

**Q: Are the 500 sites real?** No. They are representative synthetic site fixtures. Weather figures and tariffs also require source-appropriate verification.

**Q: Why invest in this?** Only if a controlled field pilot demonstrates lower review effort with an acceptable false-clearance rate and practical deployment costs.
