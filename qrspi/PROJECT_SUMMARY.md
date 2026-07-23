# MAIC Nexus Challenge: Mandatory Project Summary

**Project Name:** Heliopolis-AI (Solar Project Intelligence Agent)  
**Track Selected:** Track T1 — AI for Clean Energy (Solarvest Holdings Berhad)  
**Team Location:** Multimedia University (MMU), Melaka, Malaysia  

---

## 1. Executive Summary
Heliopolis-AI is an engineering-grade, neural-symbolic software agent designed to accelerate clean energy site selection, legal due diligence, and electrical grid compliance for Utility-Scale Solar (LSS) and Commercial & Industrial (C&I) project developers in Malaysia. By replacing manual, error-prone administrative workflows with automated, deterministic parsing, Heliopolis-AI supports Malaysia's green transition under the **National Energy Transition Roadmap (NETR)**.

---

## 2. Core Problem & Industry Pain Points
Clean energy developers face immense operational friction during project intake:
* **The Land Bottleneck:** Translating archaic scanned land titles (*Geran*), calculating fractured co-owner tenant-in-common splits, checking Malay Reserve Land blocks, and assessing land-use conversions under National Land Code Section 124.
* **The Electrical Grid Bottleneck:** Manually checking CAD single-line diagrams (SLDs) for compliance with the **TNB Electricity Supply Application Guide (ESAG)** and **MS 1837:2010** safety codes. Mistakes lead to costly, time-consuming grid rejections.
* **The Valuation Gap:** Standard due diligence ignores high-resolution contour slopes, resulting in unforeseen grading costs and monsoonal landslide risks post-acquisition.

---

## 3. Our Technological Solution
Heliopolis-AI implements a **Hybrid Neural-Symbolic Architecture** that separates perception from reasoning so that engineering, legal, and financial computations are deterministic and auditable:
1. **Legal Parser Unit:** Automatically extracts metadata from scanned land titles, programmatically converts British imperial measurements (*Ekar, Rood, Pole*) to metric *hectares* and *square meters*, and calculates co-owner fractional share matrices to verify if a controlling interest ($\ge 51\%$) exists.
2. **Civil Slope Analyzer:** Uses 2D spatial finite differences (`np.gradient`) on topography grids to compute slope gradients, classifying terrain and automatically adjusting CAPEX budgets with soil retention and earthworks premiums.
3. **SLD Graph Resolver:** Detects electrical symbols using **Gemini Vision OCR**, segments branches, and runs an $\epsilon$-neighbor search algorithm to construct a directed graph in **NetworkX**. It programmatically audits the netlist against TNB anti-islanding grid guidelines.
4. **Financial Sizing Engine:** Simulates tropical temperature operating losses ($12\%$ cell derating) and annual performance degradation ($0.5\%$), solving Levelized Cost of Electricity (LCOE), Net Present Value (NPV), and Internal Rate of Return (IRR) via a Newton-Raphson solver.
5. **Regulatory Manifest Generator:** Prefills SEDA Rakyat/NOVA forms and automatically flags mandatory **SEDA NEMAS** study requirements if generation exceeds **72 kWac**.

---

## 4. Business Model & Market Viability
Heliopolis-AI operates on a **B2B SaaS Licensing Model**:
* **Target Audience:** Engineering, Procurement, and Construction (EPC) solar contractors, Independent Power Producers (IPPs), and real-estate land search consultancies in Peninsular Malaysia.
* **Pricing Tier:** Multi-tier monthly subscriptions based on transaction lookup volume, with custom API integration tiers for utility players like Solarvest.
* **Unfair Advantage:** Built as a highly specialized, clean-room physical engineering agent, Heliopolis-AI is completely immune to generic document processing competitors, solving critical, domain-specific grid-code and land administrative mathematics.
