# MAIC Nexus Challenge: Mandatory Project Summary

**Project Name:** Heliopolis-AI (Solar Project Intelligence Agent)  
**Track Selected:** Track T1 — AI for Clean Energy (Solarvest Holdings Berhad)  
**Team Location:** Multimedia University (MMU), Melaka, Malaysia  
**GitHub Repository:** https://github.com/lewbei/heliopolis-ai  
**Live Demo (Streamlit):** Run `streamlit run app.py` locally after cloning the repo.  

---

## 1. Executive Summary

Heliopolis-AI is an engineering-grade, hybrid neural-symbolic software agent that automates clean-energy site screening, legal land due diligence, and electrical grid compliance for Utility-Scale Solar (LSS) and Commercial & Industrial (C&I) project developers in Malaysia.

By separating **multimodal perception** (Gemini Vision OCR for scanned land titles and single-line diagrams) from **deterministic symbolic reasoning** (land-share math, finite-difference slope analysis, NetworkX grid-code audits, and Newton-Raphson financial modelling), Heliopolis-AI produces auditable, bankable site assessments in minutes instead of weeks.

The project directly supports Malaysia’s **National Energy Transition Roadmap (NETR)** by accelerating the screening and grid-connection of solar assets.

---

## 2. Core Problem & Industry Pain Points

Solar developers in Malaysia lose 2–6 weeks on every project intake because critical data is trapped in unstructured, domain-specific documents:

* **The Land Bottleneck:** Scanned *Geran* land titles use archaic imperial units (*Ekar, Rood, Pole*), list fragmented tenant-in-common co-owners, and may carry Malay Reserve Land, Caveat (*Kaveat*), or Charge (*Gadaian*) restrictions. Manual review is slow and error-prone.
* **The Electrical Grid Bottleneck:** CAD single-line diagrams (SLDs) must be checked against **TNB ESAG** and **MS 1837:2010** before submission. Missing an anti-islanding relay or misreading a busbar connection can trigger expensive grid rejections.
* **The Valuation Gap:** Standard due diligence often ignores high-resolution terrain slopes. Sites that look flat on satellite imagery can hide >15° slopes, triggering unbudgeted earthworks and monsoonal landslide risk.
* **The Financial Uncertainty:** A single tariff assumption is not enough. An LSS PPA at RM 0.17/kWh, a C&I NEM/ATAP offset at ~RM 0.37/kWh, and a premium self-consumption tariff at ~RM 0.45/kWh produce radically different NPVs, but most tools cannot switch between them.

---

## 3. Our Technological Solution

Heliopolis-AI implements a **Hybrid Neural-Symbolic Architecture**:

1. **Legal Parser Unit** (`LandTitleParser`): Converts imperial land area units to metric hectares and square meters; computes co-owner share matrices and flags controlling-interest, caveats, charges, and Malay Reserve land.
2. **Civil Slope Analyzer** (`CivilSlopeAnalyzer`): Uses 2D spatial finite differences to compute slope gradients, classifies terrain as Optimal / Manageable / Critical, and applies earthworks CAPEX premiums for severe slopes.
3. **SLD Graph Resolver** (`SLDTopologyResolver`): Detects electrical symbols via Gemini Vision OCR, constructs a directed graph in NetworkX using scale-invariant ε-neighbor search, and verifies TNB anti-islanding and transformer-to-grid paths. It now also splits wire segments at detected junction dots and ignores plain line crossings, preventing short-circuit hallucinations.
4. **Financial Sizing Engine** (`YieldFeasibilityEngine`): Models tropical temperature derating, annual degradation, OPEX inflation, and BESS premiums; solves LCOE, NPV, and IRR with a robust Newton-Raphson solver.
5. **Regulatory Manifest Generator** (`FormFiller`): Pre-fills SEDA Rakyat/NOVA forms and TNB grid-connection requests, and triggers a SEDA NEMAS checklist when AC capacity exceeds 72 kWac.
6. **Interactive Streamlit Frontend** (`app.py`): Lets users adjust land attributes, restrictions, project company, technical specifications, and financial scenarios in real time, with input validation and instant visual feedback.

---

## 4. Competitive Differentiation

* **Deterministic math, not LLM guessing:** Unit conversions, share splits, graph routing, and financial cash flows are computed programmatically, so the outputs are auditable and bankable.
* **Junction-dot-aware SLD parsing:** Prevents the common failure mode where crossing busbars are incorrectly merged into one electrical net.
* **Scenario-based finance:** Users can switch between LSS PPA, C&I NEM/ATAP, and self-consumption tariffs to match the deal structure.
* **Malaysian domain specificity:** Built around the National Land Code 1965, TNB ESAG/MS 1837, and real Peninsular Malaysia meteorological data.
* **Offline-capable core:** The symbolic solvers run entirely locally; only the optional OCR perception step calls the Gemini Vision API.

---

## 5. Business Model & Market Viability

**Target customers:** EPC solar contractors, Independent Power Producers (IPPs), and land-search consultancies in Peninsular Malaysia.

**Go-to-market:**
* **Pilot:** Propose a 3–5 site pilot with Solarvest Innovation Lab or a regional EPC to validate time-savings and accuracy against manual due diligence.
* **Revenue model:** B2B SaaS licensing tiered by site-screening volume, plus enterprise API integrations for large EPCs and IPPs.
* **Unfair advantage:** Deep, clean-room domain logic that generic document-processing tools cannot easily replicate.

---

## 6. Traction & Verification

* **Repository:** https://github.com/lewbei/heliopolis-ai (public)
* **Tests:** 28 unit and integration tests passing (`pytest tests/`)
* **Working demo:** Streamlit app loads and passes health checks (`/_stcore/health` returns 200)
* **Sample output:** `solar_assessment_report.json` generated by `python solar_agent.py` shows a positive-NPV C&I NEM/ATAP demo project (NPV RM 10.5M, IRR 12.38%).
* **Compliance portfolio:** Complete `qrspi/` documentation including QRSPI contract, research pack, design options, red-team audit, and FTO assessment.

---

## 7. Team

The team is based at **Multimedia University (MMU), Melaka, Malaysia**, and combines software engineering, clean-energy domain research, and Malaysian regulatory knowledge. All core code is a clean-room implementation built on open-source libraries (NumPy, NetworkX, Pydantic, Matplotlib, Plotly, Streamlit, Google GenAI).

---

## 8. Submission Artifacts

* **Project Summary:** This document (`qrspi/PROJECT_SUMMARY.md`)
* **AI Usage Disclosure:** `qrspi/AI_USAGE_DISCLOSURE.md`
* **Pitch Deck:** `PITCH_DECK.md` and `pitch_deck.pdf` (in repo root)
* **Source Code:** `solar_agent.py`, `app.py`, `app_logic.py`, `heliopolis_ocr.py`, `solar_visualizer.py`
* **Tests:** `tests/` (28 passing)
* **Compliance docs:** `qrspi/` folder
* **Demo:** `streamlit run app.py` (optional artifact link can be added later from the team dashboard)

---

## 9. Call to Action

We are seeking:
1. A **pilot deployment** with Solarvest Innovation Lab or a Malaysian solar EPC to validate the agent on 3–5 live site opportunities.
2. **Investment / prize support** to integrate live e-Tanah / myTNB / SEDA portal APIs and deploy a hosted SaaS version.
3. **Mentorship** from the MAIC Nexus and HATI network on enterprise sales and regulatory partnerships.

Heliopolis-AI turns weeks of manual solar due diligence into auditable, minutes-long intelligence — and helps Malaysia build its clean-energy future faster.
