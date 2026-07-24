# Heliopolis-AI — Pitch Deck

**Track T1: AI for Clean Energy (Solarvest Holdings Berhad)**  
**MAIC Nexus Challenge 2026**

---

## Slide 1 — Title

# Heliopolis-AI
## Solar Project Intelligence Agent

**Engineering-grade, neural-symbolic due diligence for LSS & C&I solar in Malaysia.**

*Multimedia University (MMU), Melaka, Malaysia*  
*GitHub: https://github.com/lewbei/heliopolis-ai*

---

## Slide 2 — The Problem

Solar developers in Malaysia lose **2–6 weeks** on every new site intake.

| Bottleneck | Why it hurts |
|---|---|
| **Land Titles** | *Geran* scans use archaic *Ekar/Rood/Pole* units, fractured co-owners, and hidden Caveat/Charge/Malay-Reserve flags. |
| **Grid Compliance** | SLDs must satisfy **TNB ESAG / MS 1837:2010**; errors = expensive rejections. |
| **Terrain Risk** | Satellite photos hide >15° slopes and monsoon landslide hazards. |
| **Finance** | LSS PPA, C&I NEM, and self-consumption tariffs give completely different NPVs — but most tools only assume one. |

Result: slow screening, missed red flags, and bad capital allocation.

---

## Slide 3 — The Solution

**Heliopolis-AI** automates land, grid, terrain, and financial due diligence in one auditable pipeline.

```
[ Scanned Deed / SLD ]
         │
   Gemini Vision OCR
         │
   ├─ Legal Parser      (NLC 1965, share splits, imperial → metric)
   ├─ Civil Slope       (2D finite-difference gradients)
   ├─ SLD Graph         (NetworkX + TNB anti-islanding audit)
   └─ Financial Engine  (LCOE / NPV / IRR by scenario)
         │
[ SEDA + TNB Prefilled Manifests ]
```

**All math is deterministic — no LLM hallucination on engineering or finance.**

---

## Slide 4 — Product Demo

Run `python solar_agent.py` → `solar_assessment_report.json`

**Example output (C&I NEM / ATAP scenario):**

| Metric | Value |
|---|---|
| Site | Johor, 9.3 ha (22 Ekar 3 Rood 38 Pole) |
| DC Capacity | 6.90 MWp |
| Annual Yield | ~10,600 MWh/year |
| Final CAPEX | RM 20.7M |
| NPV (21 yrs) | **RM 10.5M** |
| IRR | **12.38%** |
| Land Legal Status | Flagged/Risky (Pertanian → needs NLC §124 conversion) |
| BESS Required | No (substation injection < 15%) |
| NEMAS Required | Yes (>72 kWac) |
| Applicant | Solarvest Development Sdn Bhd |

---

## Slide 5 — How It Works: 6 Modules

1. **Legal Parser** — reads title no, lot, state, zoning, area, co-owner shares.
2. **Slope Analyzer** — finite-difference terrain gradients + earthworks premium.
3. **SLD Graph Resolver** — symbol detection → directed graph → TNB compliance.
4. **Financial Engine** — tropical derating, degradation, BESS OPEX, Newton-Raphson IRR.
5. **Scenario Selector** — LSS PPA / C&I NEM / self-consumption tariffs.
6. **Manifest Generator** — SEDA & TNB pre-filled forms + NEMAS checklist.

---

## Slide 6 — Technical Moat

**Why this is hard to copy:**

* **Junction-dot-aware SLD parsing** — splits wires at real connection dots and ignores plain crossings, preventing short-circuit hallucinations.
* **Scale-invariant ε-neighbor search** — works across A4 to A0 drawings.
* **Scenario-based finance** — one model, three revenue realities.
* **Malaysian legal domain** — NLC 1965, *Ekar/Rood/Pole*, caveats, Malay Reserve, SEDA NEMAS.
* **Offline core** — symbolic solvers run locally; OCR is the only cloud call.

---

## Slide 7 — Market & Business Model

**Target customers:**
* Solar EPC contractors
* Independent Power Producers (IPPs)
* Land-search / due-diligence consultancies

**Go-to-market:**
1. **Pilot** with Solarvest Innovation Lab or a regional EPC — 3–5 live sites.
2. **B2B SaaS** tiered by site-screening volume.
3. **Enterprise API** for large EPCs / IPPs.

**Revenue:** subscriptions + integration fees.

---

## Slide 8 — Traction

* ✅ **28/28** unit & integration tests passing (`pytest tests/`)
* ✅ Streamlit app passes health checks (`/_stcore/health` = 200)
* ✅ Public GitHub repo: `https://github.com/lewbei/heliopolis-ai`
* ✅ Complete QRSPI compliance folder (`qrspi/`)
* ✅ Sample `solar_assessment_report.json` with positive-NPV demo
* ✅ Visual outputs: slope map + SLD graph in `qrspi/plots/`

---

## Slide 9 — Visual Proof

**Terrain Slope Risk Map**
*Identifies flat, manageable, and critical slope zones with earthworks cost premiums.*

`qrspi/plots/perak_slope_risk_contour.png`

**SLD Topology Flow Graph**
*Directed graph verifying TNB anti-islanding and transformer-to-grid connectivity.*

`qrspi/plots/sld_topology_flow_graph.png`

---

## Slide 10 — Team

**Multimedia University (MMU), Melaka, Malaysia**

* Software engineering + clean-energy domain research
* Malaysian regulatory & land-code knowledge
* Clean-room code built on NumPy, NetworkX, Pydantic, Matplotlib, Plotly, Streamlit, Google GenAI

---

## Slide 11 — Ask

We are seeking:

1. **Pilot partner** — Solarvest Innovation Lab or a Malaysian EPC to validate on 3–5 live sites.
2. **Investment / prize support** — to build live e-Tanah / myTNB / SEDA integrations and a hosted SaaS.
3. **MAIC Nexus + HATI mentorship** — on B2B sales and regulatory partnerships.

**Heliopolis-AI turns weeks of manual solar due diligence into auditable, minutes-long intelligence.**

---

## Slide 12 — Closing

# Thank you

**Heliopolis-AI**  
*Solar Project Intelligence Agent for Malaysia*

🌐 GitHub: https://github.com/lewbei/heliopolis-ai
