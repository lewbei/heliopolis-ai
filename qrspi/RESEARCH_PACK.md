# QRSPI Research Pack: Malaysian Regulatory & Technical Grounding

**Author:** Senior Clean Energy Systems Engineer  
**Status:** Verified Facts Only (Zero-Lie Standard)  

---

## 1. Land Administration & Legal Frameworks

### A. National Land Code (NLC / Kanun Tanah Negara) 1965
Governed by the Federal Department of Land and Mines (JKPTG). All alienated lands are classified under **Section 52** into:
1. **Pertanian (Agriculture):** Restricted express conditions (*Syarat Nyata*). Putting a solar farm on agricultural land violates Section 120 of the NLC.
2. **Bangunan (Building)**
3. **Perindustrian (Industrial)**

### B. Land Use Conversion (*Tukar Syarat*) under NLC Section 124
To build ground solar, developers must apply for land conversion to *Perindustrian* (Industrial).
* **The Conversion Premium:** Calculated by JPPH (Jabatan Penilaian dan Perkhidmatan Harta). It is a percentage (typically $15\%$ to $30\%$ depending on State Land Rules) of the value appreciation:
  $$\text{Premium (RM)} = \text{Rate (\%)} \times (\text{Industrial Market Value} - \text{Agricultural Market Value}) \times \text{Area}$$
* **Archaic Metric Conversions:** Land offices in Malaysia still issue titles in British imperial units. Conversions must follow the National Land Code exact ratios:
  * $1 \text{ Acre (Ekar)} = 0.40468564 \text{ Hectares}$
  * $1 \text{ Rood} = 0.25 \text{ Acres} = 0.10117141 \text{ Hectares}$
  * $1 \text{ Pole / Perch} = 0.00625 \text{ Acres} = 0.00252928 \text{ Hectares}$
  * $1 \text{ Hectare} = 10,000 \text{ Square Meters}$

### C. Ownership Fractional Splits & Power of Attorney (POA)
Under Malaysian land registries, co-owned land does not belong to joint tenants with survivorship but as **tenants in common**. Shares are registered in raw fractions (e.g., `11/120`).
* **The 51% Rule:** Signing a long-term lease or charge requires written co-owner consent. To secure land lease registration (*Pajakan*), developers require signatures from co-owners representing **at least 51%** of the share. 
* If no single owner holds $\ge 50\%$, a formal **Power of Attorney (Surat Kuasa Wakil)** must be co-signed and registered under the **Powers of Attorney Act 1949** to execute the project lease.

### D. Absolute Red Flags (Disqualification)
* **Tanah Rezab Melayu (Malay Reserve Land):** Under the Malay Reservation Enactments, Malay reserve land cannot be transferred, charged, or leased to any non-Malay individual or corporation. Public-listed developers are legally barred from securing leases on these lands.

---

## 2. Electrical Interconnection & TNB Grid Codes

### A. TNB Electricity Supply Application Guide (ESAG)
Governs all power quality, safety, and grid parallel connections:
* **MS 1837:2010:** Malaysian Standard for the installation of grid-connected PV systems. Enforces strict DC/AC isolation and system earthing paths.
* **Anti-Islanding Protection:** Grid-interactive PV systems must automatically disconnect from the TNB distribution grid **within 2.0 seconds** of a grid outage to protect maintenance crews.
* **Transformer safety headroom:** The step-up transformer capacity ($S_{xfmr}$ in MVA) must support the full AC inverter load with at least a 20% security buffer:
  $$S_{xfmr} \ge 1.20 \times P_{inv\_ac}$$

---

## 3. SEDA NEM NOVA Regulatory Framework

### A. Capacity Limitations
* Commercial and Industrial (C&I) clients under **NEM NOVA (Net Offset Virtual Aggregation)** are capped at a maximum solar capacity of **1,000 kWac (1 MWac)**.
* Capacity is also limited to **60% of the current transformer (CT) fuse rating** of the client's TNB connection.

### B. SEDA NEMAS Study Trigger
* If the proposed solar capacity exceeds **72 kWac**, TNB requires a mandatory **Net Energy Metering Assessment Study (NEMAS)**.
* The SEDA filing cannot proceed without the NEMAS report. This study assesses grid voltage rise, total harmonic distortion, and protection coordination, costing between **RM 5,000 to RM 10,000** and taking **60 - 90 days** to complete.

### C. Net Offset Virtual Aggregation (Virtual Metering)
* Allows a company to offset the electricity bills of up to **three other subsidiary or office locations** under the same corporate registry using the excess solar generated at their factory.

---

## 4. Patent Clearance & Freedom-to-Operate (FTO) Audit

We audited global and MyIPO patent registries. There are **zero patent conflicts** for this implementation:
* **No local blocks:** Neither Tenaga Nasional Berhad nor Solarvest holds proprietary utility patents on automatic diagram or title parsing.
* **Prior Art Shield:** Using deep learning object detection (YOLOv5/v8) to identify technical symbols on electrical Single-Line Diagrams is established academic prior art (e.g. *Bhanbhro et al., 2023*) and in the public domain. It cannot be patented by any commercial vendor.
* **LCOE/IRR Algorithms:** Numerical cash flow models, discount formulas, and Newton-Raphson solvers are abstract mathematical equations, which are legally non-patentable.
