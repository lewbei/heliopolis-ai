# MAIC Nexus Challenge: Mandatory AI Usage Disclosure

**Project Name:** Heliopolis-AI (Solar Project Intelligence Agent)  
**Track Selected:** Track T1 — AI for Clean Energy (Solarvest Holdings Berhad)  
**Security / IP Status:** Freedom-to-Operate assessment completed; no obvious overlap identified in reviewed patent families.  

---

## 1. Algorithmic Overview & Scope of AI
Heliopolis-AI utilizes artificial intelligence exclusively for **visual perception and spatial layout segmentation**, while reserving all mathematical modeling, safety checking, and financial accounting to **deterministic, symbolic algorithms**. This design prevents LLM hallucinations, ensuring civil and electrical engineering accuracy.

---

## 2. Upstream AI Models & Frameworks Used
We declare the following open-source, industry-standard models and libraries used within our pipeline:

1. **Gemini Vision (Google GenAI / Vertex AI):**
   * **Role:** Extracts structured metadata and electrical symbol bounding boxes from scanned land titles (*Geran*) and Single-Line Diagram raster images via multimodal prompting.
2. **NetworkX (BSD License):**
   * **Role:** Constructs directed topological graphs from symbol coordinates and wiring line segments (resolved via Euclidean spatial $\epsilon$-search), solving path routing programmatically.
3. **Pydantic V2 (MIT License):**
   * **Role:** Enforces runtime type-safety and JSON schemas for all output data models.

---

## 3. Proprietary Clean-Room Code & Logic (Built From Scratch)
The following modules represent our team's original, clean-room implementation, built on open-source libraries and containing no copied university codebases:
* **`LandTitleParser` (Imperial-to-Metric & Share Splits):** Original coordinate translation math and fractional share matrix co-ownership logic conforming to the **National Land Code 1965**.
* **`CivilSlopeAnalyzer` (2D Spatial Gradient):** Original elevation contour slope solver using finite differences.
* **`SLDTopologyResolver` ($\epsilon$-Search Solver):** Original wire segment proximity-neighbor matcher and TNB protection relay flow checker.
* **`YieldFeasibilityEngine` (Newton-Raphson Solver):** Original tropical temperature derating cashflow model and iterative IRR solver.

---

## 4. Intellectual Property & Freedom-to-Operate (FTO)
We have audited local and global patent databases. We declare that Heliopolis-AI does not violate any active utility patents or copyrights:
* All financial equations and administrative conversions are mathematical abstractions, which are legally non-patentable.
