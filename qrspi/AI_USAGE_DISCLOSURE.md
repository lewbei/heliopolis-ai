# MAIC Nexus Challenge: Mandatory AI Usage Disclosure

**Project Name:** Heliopolis-AI (Solar Project Intelligence Agent)  
**Track Selected:** Track T1 — AI for Clean Energy (Solarvest Holdings Berhad)  
**Security / IP Status:** 100% Cleared (Freedom-to-Operate Confirmed)  

---

## 1. Algorithmic Overview & Scope of AI
Heliopolis-AI utilizes artificial intelligence exclusively for **visual perception and spatial layout segmentation**, while reserving all mathematical modeling, safety checking, and financial accounting to **deterministic, symbolic algorithms**. This design prevents LLM hallucinations, ensuring civil and electrical engineering accuracy.

---

## 2. Upstream AI Models & Frameworks Used
We declare the following open-source, industry-standard models and libraries used within our pipeline:

1. **YOLOv8 (Ultralytics - AGPL License):** 
   * **Role:** Detects and classifies 2D electrical symbol bounding boxes (PV Arrays, Inverters, Transformers, Protective Relays, Grid Connection points) in Single-Line Diagram raster images.
   * **Customization:** Fine-tuned on standard electrical symbol datasets.
2. **PaddleOCR / PP-StructureV3 (Baidu - Apache 2.0 License):**
   * **Role:** Segments the structural layout of land title searches (*Geran*), detecting table boundaries and extracting raw text coordinates.
3. **NetworkX (BSD License):**
   * **Role:** Constructs directed topological graphs from symbol coordinates and wiring line segments (resolved via Euclidean spatial $\epsilon$-search), solving path routing programmatically.
4. **Pydantic V2 (MIT License):**
   * **Role:** Enforces runtime type-safety and JSON schemas for all output data models.

---

## 3. Proprietary Clean-Room Code & Logic (Built From Scratch)
The following modules represent our team's original, clean-room implementation, containing no copyrighted, patented, or plagiarized university codebases:
* **`LandTitleParser` (Imperial-to-Metric & Share Splits):** 100% original coordinate translation math and fractional share matrix co-ownership logic conforming to the **National Land Code 1965**.
* **`CivilSlopeAnalyzer` (2D Spatial Gradient):** 100% original elevation contour slope solver using finite differences.
* **`SLDTopologyResolver` ($\epsilon$-Search Solver):** 100% original wire segment proximity-neighbor matcher and TNB protection relay flow checker.
* **`YieldFeasibilityEngine` (Newton-Raphson Solver):** 100% original tropical temperature derating cashflow model and iterative IRR solver.

---

## 4. Intellectual Property & Freedom-to-Operate (FTO)
We have audited local and global patent databases. We declare that Heliopolis-AI does not violate any active utility patents or copyrights:
* Broad computer vision frameworks (YOLO/PaddleOCR) are public domain assets, and using deep learning to recognize single-line diagram symbols is documented academic **Prior Art** (*Bhanbhro et al., 2023*).
* All financial equations and administrative conversions are mathematical abstractions, which are legally non-patentable.
