# QRSPI Red-Team Audit: Vulnerabilities & Failure-Proofing

**Document Ref:** RED-MAIC-NEXUS-T1-01  
**Lead Auditor:** Senior Deep Learning & Clean Energy Systems Architect  
**Classification:** Proprietary / Legal Compliance  
**Objective:** Identify the 5 critical failure modes of Heliopolis-AI and provide the technical and commercial shields to improve robustness.  

---

## 1. Failure Mode 1: The "Hatching & Overlapping" CAD Vector Collapse
* **The Vulnerability (Technical):**
  * Single-Line Diagrams (SLDs) frequently contain line-crossings (busbar overlaps), nested components, or overlapping text elements.
  * Our current spatial $\epsilon$-neighbor search connects segment endpoints to bounding boxes. If two busbars overlap or cross at $90^\circ$ *without* a physical connection, the line segment detector (LSD) will extract them as intersecting. Our graph resolver will treat them as a single connected node, merging two independent electrical circuits.
  * *The Consequence:* A **Short-Circuit Hallucination** in the electrical topology graph. This is highly dangerous and would fail Solarvest's technical verification.
* **The Failure-Proofing Shield:**
  * **Junction Dot Verification:** Implement a secondary CV filter (using Hough Circles or a specialized CNN) to detect the physical electrical junction connection dot ($\bullet$). 
  * Only add an edge between intersecting lines in the NetworkX graph if a connection dot is physically detected at the intersection point. If lines cross without a dot, treat them as non-connected overlaps.

---

## 2. Failure Mode 2: The "Archaic Malay Legal Jargon" Semantic Drift
* **The Vulnerability (Legal):**
  * Historical land titles (*Geran*) in rural Peninsular Malaysia (especially from Perak or Kedah) do not always use standardized modern legal keywords. They often use archaic, localized, jawi-derived, or non-standard administrative Malay phrasing.
  * *For example:* Phrasings like *"Sekatan: tanah ini tidak boleh dipindahmilik melainkan setelah mendapat kelulusan khas Kebawah Duli Yang Maha Mulia Sultan"* or *"tiada amanah boleh didaftarkan."*
  * *The Consequence:* Standard regex pattern matchers (`Kaveat`, `Gadaian`, `Rezab Melayu`) will **silently skip** these archaic blocks. Heliopolis-AI will mark the land status as "Approved" instead of "Flagged/Rejected," exposing Solarvest to millions of Ringgit in legal blocking orders post-acquisition.
* **The Failure-Proofing Shield:**
  * **Semantic Legal Auditor Fallback:** Integrate a local lightweight LLM or the same Gemini Vision OCR pipeline to perform Named Entity Recognition (NER) on legal land restrictions when pattern-matching confidence is low.
  * If the pattern-matching confidence is low or a non-standard restriction is detected, the agent automatically flags the title for **Human-in-the-Loop (HITL)** legal review on the web canvas.

---

## 3. Failure Mode 3: The "Tropical PV Degradation Curve" Nonlinearity
* **The Vulnerability (Financial):**
  * Standard financial models assume a linear annual PV module degradation (e.g., $d = 0.5\%$).
  * *The Reality:* Tropical climates (high humidity, monsoonal dust, extreme heat) trigger **highly non-linear degradation** due to Light Induced Degradation (LID) and Potential Induced Degradation (PID).
  * *The Consequence:* Sizing models will over-predict generation in the early years and under-predict in later years, leading to a mismatched cash flow model that breaks bankability audits during project financing.
* **The Failure-Proofing Shield:**
  * **Tropical Non-Linear Degradation Model:** Replace linear degradation with a piecewise, non-linear degradation array:
    * **Year 1:** $1.5\%$ loss (LID).
    * **Years 2–10:** $0.6\%$ annual loss.
    * **Years 11–15:** $0.8\%$ annual loss.
    * **Years 16–21:** $1.2\%$ annual loss (accounting for cable degradation and inverter drying).

---

## 4. Failure Mode 4: SEDA NOVA "Corporate Registry" Loopholes
* **The Vulnerability (Regulatory):**
  * A corporate client attempts to aggregate meters across different offices or factories under **NEM NOVA Net Offset Virtual Aggregation**.
  * *The Reality:* SEDA guidelines strictly mandate that virtual meter aggregation is **only allowed for entities registered under the exact same SSM (Companies Commission of Malaysia) corporate registration number**.
  * *The Consequence:* If a parent company attempts to aggregate meters from separate subsidiaries registered under different SSM numbers, SEDA will reject the application, causing months of filing delays and wasting SEDA submission fees.
* **The Failure-Proofing Shield:**
  * **SSM Corporate Registration Matcher:** Before generating the prefilled SEDA manifest, the agent must extract and cross-reference the SSM corporate numbers of all virtually aggregated TNB meters, blocking the generation if there is an entity mismatch.

---

## 5. Failure Mode 5: The "VC Blind Spot" (Over-Engineering the Pitch)
* **The Vulnerability (Commercial/Pitch):**
  * The team spends 80% of the presentation explaining the NetworkX directed graph algorithms and 2D finite difference slope gradients, and only 20% explaining the commercial cash impact.
  * *The Consequence:* C-level judges (Venture Capitalists and Solarvest's CEO) will tune out. They care about **Margin, Customer Acquisition Costs (CAC), and Internal Rate of Return (IRR)**. They will assume you are "academic researchers" who cannot run a business, and give the prize to a less-technical team with a slicker commercial story.
* **The Failure-Proofing Shield:**
  * **The 80/20 Pitch Rule:**
    * **20% Technical (The Mic Drop):** Show the NetworkX graph and regulatory manifest generation as a 10-second demo. This demonstrates a credible technical moat.
    * **80% Commercial (The Value):** Focus on how Heliopolis-AI can reduce land and grid due-diligence effort, cut administrative rework, and accelerate pipeline screening for Solarvest's CGPP/LSS projects. Quote specific savings only after a pilot validates them.
