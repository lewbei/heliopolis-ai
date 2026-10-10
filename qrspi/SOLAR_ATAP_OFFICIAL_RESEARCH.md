# Solar ATAP — verified sources and Heliopolis implementation boundary

**Research date:** 10 October 2026.  
**Scope:** Non-domestic consumer rooftop solar energy-component calculation, not LSS ground-mounted project due diligence, full TNB billing, company legal advice, or a bankable financial forecast.

## Official sources

1. [Energy Commission, GP/ST/No. 60/2025, Solar ATAP Guidelines (44-page PDF)](https://www.st.gov.my/sites/default/files/2026-03/GUIDELINES-FOR-SOLAR-ACCELERATED_0.pdf): effective 1 January 2026; first version dated 30 December 2025.
2. [SEDA Solar ATAP programme portal](https://www.seda.gov.my/reportal/atap/): capacity/technical assessments and downloadable forms; 2026 contract link.
3. [SEDA Solar ATAP customer load-profile example form](https://www.seda.gov.my/reportal/wp-content/uploads/2025/12/3.-Load-Profile-sample-form.pdf): **blank template, NOT a real consumer dataset**.
4. [Malaysia Single Buyer: SMP for NEM NOVA & Solar ATAP](https://www.singlebuyer.com.my/market/market-data/system-marginal-price): official prior-month daytime Average SMP. It publicly records revised January 2026 RM0.1911/kWh and February 2026 RM0.1893/kWh, replacing earlier published RM0.1849 and RM0.1832 respectively. Those **historical** numbers are not assumed to be today's SMP.
5. [TNB Solar ATAP contract (April 2026)](https://www.seda.gov.my/reportal/wp-content/uploads/2026/04/Solar-ATAP-Contract_Complete-v1.1.pdf).

The official PDF should be considered the source of truth where marketing/blog summaries disagree. Check for subsequent amendments at the time of a real application.

## Important programme separation

Solar ATAP is intended for PV on the consumer's **rooftop** at its premises; the guideline also allows solar carparks and covered walkways inside that compound (clause 7). Do not re-label Heliopolis' simulated **ground-mounted, multi-MW LSS land prospecting** as Solar ATAP.

Non-domestic inverter output is limited to min(100% of applicable Maximum Demand, 1,000 kWac), subject to utility technical studies and eligibility (clause 8). For existing consumer records, MD is the average recorded over the last 12 months; a declared MD is allowed with less than 12 months of record. Inputting an MD into Heliopolis is **not proof** it was verified by TNB.

Users with NEM/SelCo contracts may be able to transition by terminating the earlier contract subject to the stated rules (sections 1 and 6); an unconditional ban on all existing solar consumers would overstate the guidelines. Co-generators/back-feeders and multi-tenant consumers face separate restrictions.

## Exact energy-only settlement logic

In the official guideline:
- **Clause 2 (definitions):** Maximum Allowable Quantity (MAQ, in kWh) = proposed inverter kWac × 5 sun hours/day × days in the actual billing period.
- **Clauses 3.6, 13, 14:** The non-domestic exported-energy credit uses **Average SMP**, the 07:00–19:00 average of the **preceding calendar month**. For a model billing period:
  - eligible export kWh = min(grid export kWh, MAQ, grid import kWh);
  - nominal credit RM = eligible export kWh × preceding-month Average SMP;
  - usable credit RM = min(nominal credit RM, grid import kWh × applicable Energy Charge RM/kWh);
  - net energy charge RM = max(0, import energy charge − usable credit).
- **Unutilized export/credit is forfeited within the billing period.** It does not carry over or become a cash payment, and it does not reduce the Automatic Fuel Adjustment or other non-energy components.
- **Clause 4:** ATAP credit term is up to **10 years**; afterward strictly self-consumption rules apply and excess export is not credited.
- **Clause 15.3:** separate one-time **application fee RM7.50 per kW**. Technical studies/fees are a different cost; no inference of project technical approval.

This is an energy-component **screen**; a retail tariff may have other charges, rebates, tiers, or actual billing details, and is not replaced by an average flat energy rate in a bankable invoice. For 2026 reference, see also SEDA technical-assessment table (CAS by LV/MV capacity and PSS for HV).

## Data necessary for a real feasibility evaluation

- TNB bill and tariff/energy-charge component, eligible TNB consumer status and signed/approved Solar ATAP contract.
- MD evidence, connection voltage and approved AC inverter size.
- Actual **time-aligned load data and PV generation or credible timestamped forecast** for every model interval. A single annual yield number cannot determine simultaneous on-site PV use and excess exports.
- Metered monthly imports and exports (or predictions aggregated from consistent intervals); actual billing day counts.
- The preceding month's **published Average SMP for each billing month**, with exact reference date/version from Single Buyer.
- Customer contract start/end dates; no assumed post-year-10 credits.
- CAPEX/OPEX/maintenance/replacement, degradation and financing terms if an **optional** illustrative multi-year NPV is to be explored; mark all extrapolation assumptions.

The publicly available customer form is blank. No actual consented TNB billing or customer interval load dataset is present in this repository. Therefore **no production OCR accuracy, real customer bill savings or 21-year ROI is established**.

## Reproducible code, not a fabricated customer study

The standalone [monthly model](../solar_atap_settlement.py) supports a no-storage, energy-component demonstration ONLY with explicitly supplied or synthetic billing inputs. It requires actual billing days, a source month for SMP, imported/exported kWh, energy-charge rate, and an assumed MD, and will refuse over-capacity or post-term exports. [Unit tests](../tests/test_solar_atap_settlement.py) cover MAQ, imported-energy cap, cash floor, no rollover, incorrect SMP month, capacity limits, time-aligned self-consumption and the 10-year boundary.

Example data in those tests are openly **synthetic**. The model's use of exactly 120 monthly periods for a ten-year interval is a simplification; actual legal contract expiry follows its commissioning date and signed terms, not just a billing-cycle count. Real deployment must add that date check and validate source customer data.

**Open research/engineering issue #4 remains unresolved** until live profiles, authentic tariffs, settlement comparisons and operational eligibility checks are available.
