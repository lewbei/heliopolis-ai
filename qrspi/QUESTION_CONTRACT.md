# QRSPI Question Contract: Solar Project Intelligence Agent

**Goal ID:** MAIC-NEXUS-T1-01  
**Track:** Track T1 (AI for Clean Energy) — Solarvest Holdings Berhad  
**Standards Authority:** Malaysian National Land Code 1965 & TNB ESAG Grid Codes  

---

## 1. Goal Definition
The objective of this goal is to design, implement, and verify a production-grade, offline-capable **Solar Project Intelligence Agent** (`solar_agent.py`) that automates dual-layer compliance and technical prospecting for ground-mounted Utility-Scale Solar (LSS) and large Commercial & Industrial (C&I) solar site developments in Malaysia.

---

## 2. Why It Matters
Clean energy site selection in Malaysia is bottlenecked by manual due diligence:
* **The Land Bottleneck:** Teams spend weeks translating scanned land titles (*Geran*), calculating fractional co-owner splits, and assessing land-use conversions (NLC Section 124) from *Pertanian* (Agriculture) to *Perindustrian* (Industrial).
* **The Electrical Bottleneck:** CAD single-line diagrams (SLDs) are manually checked against Tenaga Nasional Berhad (TNB) grid guidelines. Minor mistakes result in expensive submission rejections.
* **The Competitive Bottleneck:** Standard document parsers (like DespaQ, the 2023 SIL winner) cannot process visual CAD schematics or handle geographic slope risks. This agent establishes an unbreachable technical moat.

---

## 3. Measurable Success Criteria

### A. Legal Ingestion & Share Splits (NLC 1965)
- [ ] Parse scanned Malaysian land titles (*Geran* or *Carian Hakmilik*) into structured metadata.
- [ ] Programmatically convert archaic imperial sizes (*Ekar, Rood, Pole*) to metric *hectares* and *square meters*.
- [ ] Sum fractional co-owner share blocks to evaluate if a controlling interest ($\ge 51\%$) exists.
- [ ] Flag Malay Reserve Land restrictions and active private Caveats (*Kaveat*) or Bank Charges (*Gadaian*).

### B. Civil Terrain & Slope Evaluation
- [ ] Process 2D spatial elevation grids using finite differences to compute slope gradients in degrees.
- [ ] Categorize terrain into Optimal ($<5^\circ$), Manageable ($5^\circ - 15^\circ$), and Critical ($>15^\circ$) zones.
- [ ] Apply a programmatic grading cost multiplier to the CAPEX if critical slope zones are active, and flag severe landslide risks ($>30^\circ$).

### C. SLD Graph & Grid-Code Compliance (TNB ESAG)
- [ ] Process symbol bounding boxes and wire layout segments.
- [ ] Implement a spatial $\epsilon$-neighbor search algorithm to construct a directed graph in **NetworkX**.
- [ ] Verify grid safety rules programmatically (presence of an active Anti-Islanding Protection Relay and valid path routing from Transformer to Grid Incomer).

### D. Financial Engineering & SEDA NOVA Triggers
- [ ] Execute a tropical temperature-derated yield model (with degradation losses).
- [ ] Solve Levelized Cost of Electricity (LCOE), Net Present Value (NPV), and Internal Rate of Return (IRR) using a deterministic Newton-Raphson solver.
- [ ] Automatically generate pre-filled regulatory manifests and trigger mandatory **SEDA NEMAS** checklists if AC generation exceeds **72 kWac**.

---

## 4. Expected Artifact Deliverables

All outputs must match these declared expected paths:
* Core Backend Script: `solar_agent.py`
* Ignored Patterns: `.gitignore`
* Final Assessment Report: `solar_assessment_report.json`
* Compliance Documentation: `qrspi/` directory
