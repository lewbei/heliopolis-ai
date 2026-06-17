# QRSPI Structure Outline: Workspace Files & Components

This document outlines the file structure, class boundaries, and artifact mappings for the **Solar Project Intelligence Agent** project, conforming to the **Path-Grounding** standard of the Mercury Goal Harness.

---

## 1. Directory Tree
```text
C:\Users\lewka\deep_learning\MAIC Nexus Challenge\
├── .git/                      # Source control tracking (Initialized)
├── .gitignore                 # Excludes caches, .env secrets, and temp PDFs/JSONs (Committed)
├── solar_agent.py             # Core executable agent script (Completed & Committed)
├── solar_assessment_report.json # Generated, auditable evaluation report (Validated)
└── qrspi/                     # Quality and Compliance verification files
    ├── QUESTION_CONTRACT.md   # Goal and measurable success criteria (Completed)
    ├── RESEARCH_PACK.md       # Legal and regulatory grounding facts (Completed)
    ├── DESIGN_OPTIONS.md      # Comparison of architectures (Completed)
    ├── STRUCTURE_OUTLINE.md   # [THIS FILE] Map of files and components
    ├── ROOT_PLAN.md           # Engineering design and mathematical specs
    └── TEST_OUTPUTS.md        # Verifier trace and behavioral test results
```

---

## 2. Component Mapping & Class Boundaries

### A. Legal Processing Unit
* **Target File:** `solar_agent.py`
* **Classes:** 
  * `OwnerModel` (Pydantic Schema): Structured registered landowner profile.
  * `PowerOfAttorneyModel` (Pydantic Schema): Fractional share joint-execution requirement manifest.
  * `LandTitleMetadata` (Pydantic Schema): Enforces metric conversions and legal risks.
  * `LandTitleParser`: Main legal text interpreter. Enforces National Land Code Sections 52 and 124.
* **Input:** Scanned land search text (*Carian Hakmilik*).
* **Output:** Validated `LandTitleMetadata` JSON payload.

### B. Civil Terrain Processing Unit
* **Target File:** `solar_agent.py`
* **Classes:**
  * `TerrainProfileModel` (Pydantic Schema): Enforces mean slope, landslide risk, and CAPEX earthwork multiplier indexes.
  * `CivilSlopeAnalyzer`: Performs 2D spatial gradients (`np.gradient`) on topography arrays.
* **Input:** 2D elevation grid array.
* **Output:** Validated `TerrainProfileModel` JSON payload.

### C. Electrical Schematic Processing Unit
* **Target File:** `solar_agent.py`
* **Classes:**
  * `SLDTopologyResolver`: Matches wire vectors to symbol bounding boxes using $\epsilon$-neighbor distance search. Programmatically checks for anti-islanding relay compliance and directed paths in NetworkX.
* **Input:** Bounding boxes of symbols and 2D coordinates of wire segments.
* **Output:** Verified Directed NetworkX Graph (`DiGraph`) adjacency list.

### D. Financial & Yield Sizing Unit
* **Target File:** `solar_agent.py`
* **Classes:**
  * `TechnicalFeasibilityModel` (Pydantic Schema): Enforces capacities, base CAPEX, adjusted CAPEX, LCOE, NPV, IRR, and payback metrics.
  * `YieldFeasibilityEngine`: Tropical temperature-derated energy yields and lifecycle cashflow solver.
* **Input:** `LandTitleMetadata` and `TerrainProfileModel` outputs.
* **Output:** Validated `TechnicalFeasibilityModel` JSON payload.

### E. SEDA & TNB Pre-filling Unit
* **Target File:** `solar_agent.py`
* **Classes:**
  * `RegulatoryFilingManifest` (Pydantic Schema): Enforces SEDA Rakyat/NOVA, TNB Grid Interconnect, and NEMAS checklists.
  * `FormFiller`: Maps technical/legal floats to SEDA and TNB application schemas.
* **Input:** Legal and Technical output payloads.
* **Output:** Completed `RegulatoryFilingManifest` payload.
