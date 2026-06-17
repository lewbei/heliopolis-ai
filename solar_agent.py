import os
import sys
import numpy as np
import networkx as nx
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OwnerModel(BaseModel):
    name: str = Field(description="Name of the registered landowner.")
    ic_or_co_no: str = Field(description="MyKad IC Number or Company Registration Number.")
    share_fraction: str = Field(description="Raw ownership share as a fraction, e.g., '11/120'.")
    calculated_share_float: float = Field(description="Decimal value of the fractional share.")

class LegalAssessmentModel(BaseModel):
    status: str = Field(description="Zoning or transaction suitability: 'Approved', 'Flagged/Risky', or 'Rejected'.")
    findings: List[str] = Field(default=[], description="List of administrative or legal issues found on the land title.")

class LandTitleMetadata(BaseModel):
    title_no: str = Field(description="Title reference number, e.g., 'GRN 45293'.")
    lot_no: str = Field(description="Lot or PT number, e.g., 'Lot 8192'.")
    state: str = Field(description="Malaysian state.")
    district: str = Field(description="District / Daerah.")
    mukim: str = Field(description="Sub-district / Mukim.")
    zoning: str = Field(description="Kategori Kegunaan Tanah, e.g., 'Pertanian', 'Bangunan', 'Perindustrian'.")
    area_imperial: str = Field(description="Raw historical imperial units, e.g., '12 Ekar 2 Rood 15 Pole'.")
    area_hectares: float = Field(description="Converted area in metric Hectares.")
    area_sq_meters: float = Field(description="Converted area in metric Square Meters.")
    owners: List[OwnerModel] = Field(default=[], description="Registered landowners with share allocations.")
    has_caveats: bool = Field(description="True if an active Caveat is detected on the title.")
    has_charges: bool = Field(description="True if an active Bank Charge (Gadaian) is detected.")
    is_malay_reserve: bool = Field(description="True if designated as Tanah Rezab Melayu.")
    legal_assessment: LegalAssessmentModel

class TechnicalFeasibilityModel(BaseModel):
    capacity_mwp: float = Field(description="Simulated PV system peak DC capacity (MWp).")
    annual_yield_mwh: float = Field(description="Estimated annual electricity generation (MWh/year).")
    estimated_capex_rm: float = Field(description="Total capital expenditure in Malaysian Ringgit (RM).")
    lcoe_rm_kwh: float = Field(description="Levelized Cost of Electricity (RM/kWh).")
    npv_rm: float = Field(description="Net Present Value (RM) over the project lifecycle.")
    irr_percent: float = Field(description="Project Internal Rate of Return (%).")
    payback_years: float = Field(description="Estimated capital payback period in years.")

class SEDAApplicationSchema(BaseModel):
    Part_A_Applicant_Name: str
    Part_A_Company_Registration: str
    Part_B_Site_Title_Number: str
    Part_B_Site_Lot_Number: str
    Part_B_Mukim_Daerah_Negeri: str
    Part_C_Proposed_DC_Capacity_kWp: float
    Part_C_Proposed_AC_Capacity_kWac: float
    Part_D_PPA_Tariff_Rate_RM_kWh: float

class TNBConnectionSchema(BaseModel):
    Applicant_Company: str
    Interconnection_Voltage_Level_kV: float
    Total_Generation_Capacity_MWac: float
    Inverter_Compliance_Standards: List[str]
    Point_of_Common_Coupling: str
    Transformer_Capacity_MVA: float

class RegulatoryFilingManifest(BaseModel):
    seda_application: SEDAApplicationSchema
    tnb_grid_request: TNBConnectionSchema


class LandTitleParser:
    """
    Simulates high-precision, layout-aware legal OCR and text analysis of Malaysian Land Titles (Geran),
    complying with the National Land Code (NLC / Kanun Tanah Negara) 1965.
    """
    @staticmethod
    def convert_imperial_to_metric(acres: float, roods: float, poles: float) -> tuple[float, float]:
        """
        Calculates precise metric conversions from archaic British imperial land units.
        Returns: (hectares, square_meters)
        """
        hectares = (acres * 0.404686) + (roods * 0.101171) + (poles * 0.002529)
        sq_meters = hectares * 10000.0
        return round(hectares, 4), round(sq_meters, 2)

    @staticmethod
    def parse_fraction(fraction_str: str) -> float:
        """
        Parses fraction strings (e.g., '11/120', 'All', 'Semua') into floating point values.
        """
        f_clean = fraction_str.strip().lower()
        if f_clean in ["semua", "all", "1", "1.0", "1/1"]:
            return 1.0
        try:
            if "/" in f_clean:
                num, denom = map(float, f_clean.split("/"))
                return num / denom
            return float(f_clean)
        except ValueError:
            return 0.0

    def parse(self, raw_ocr_text: str) -> LandTitleMetadata:
        print("[LandTitleParser] Executing layout-aware NLP metadata extraction...")
        
        # Simulated NLP Entity Extraction matches
        title_no = "GRN 45293"
        lot_no = "Lot 8192"
        state = "Perak"
        district = "Larut dan Matang"
        mukim = "Mukim Asam Kumbang"
        zoning = "Pertanian" # Agricultural, requires conversion under NLC Section 124
        
        # Converted metric values from "12 Ekar 2 Rood 15 Pole"
        hectares, sq_meters = self.convert_imperial_to_metric(acres=12.0, roods=2.0, poles=15.0)
        
        # Registered Owner Entities & Fractional Shares
        owners_raw = [
            {"name": "Ahmad Bin Ismail", "id": "650212-08-5431", "share": "1/3"},
            {"name": "Solarvest Development Sdn Bhd", "id": "1234567-U", "share": "2/3"}
        ]
        
        owners = []
        for o in owners_raw:
            float_val = self.parse_fraction(o["share"])
            owners.append(OwnerModel(
                name=o["name"],
                ic_or_co_no=o["id"],
                share_fraction=o["share"],
                calculated_share_float=round(float_val, 4)
            ))
            
        is_malay_reserve = "Tanah Rezab Melayu" in raw_ocr_text or "Rezab Melayu" in raw_ocr_text
        has_caveats = "Kaveat" in raw_ocr_text
        has_charges = "Gadaian" in raw_ocr_text or "Dichaj" in raw_ocr_text
        
        # State-level conversion and transactional risk assessment
        legal_status = "Approved"
        findings = []
        
        if zoning == "Pertanian":
            findings.append("Category 'Pertanian' requires NLC Section 124 land conversion to 'Perindustrian'.")
        if has_caveats:
            legal_status = "Flagged/Risky"
            findings.append("Active Private Caveat detected. Land transactions are frozen until formal withdrawal.")
        if has_charges:
            legal_status = "Flagged/Risky"
            findings.append("Active Bank Charge (Gadaian) detected. Requires bank consent letter prior to lease.")
        if is_malay_reserve:
            legal_status = "Rejected"
            findings.append("Tanah Rezab Melayu (Malay Reserve) cannot be legally transferred or leased to non-Malay corporate entities.")
            
        return LandTitleMetadata(
            title_no=title_no,
            lot_no=lot_no,
            state=state,
            district=district,
            mukim=mukim,
            zoning=zoning,
            area_imperial="12 Ekar 2 Rood 15 Pole",
            area_hectares=hectares,
            area_sq_meters=sq_meters,
            owners=owners,
            has_caveats=has_caveats,
            has_charges=has_charges,
            is_malay_reserve=is_malay_reserve,
            legal_assessment=LegalAssessmentModel(status=legal_status, findings=findings)
        )


class SLDTopologyResolver:
    """
    Processes symbol bounding boxes and wire layout lines to construct a directed
    topological graph, validating compliance with TNB interconnection protection rules.
    """
    def __init__(self, epsilon_px: float = 15.0):
        self.epsilon = epsilon_px

    def resolve(self, symbols: List[Dict[str, Any]], lines: List[tuple]) -> nx.DiGraph:
        print("[SLDTopologyResolver] Constructing directed topology graph...")
        g = nx.DiGraph()
        
        # Add visual components as nodes
        for sym in symbols:
            g.add_node(sym["id"], category=sym["class"], bbox=sym["bbox"])
            
        # Match lines to bounding boxes based on Euclidean distance boundaries (epsilon-neighbor search)
        for line in lines:
            pt1, pt2 = line
            u, v = None, None
            
            for node_id, data in g.nodes(data=True):
                bbox = data["bbox"]
                ymin, xmin, ymax, xmax = bbox
                
                def distance_to_box(pt, box):
                    px, py = pt
                    b_ymin, b_xmin, b_ymax, b_xmax = box
                    dx = max(b_xmin - px, 0, px - b_xmax)
                    dy = max(b_ymin - py, 0, py - b_ymax)
                    return np.sqrt(dx**2 + dy**2)
                
                if distance_to_box(pt1, bbox) <= self.epsilon:
                    u = node_id
                if distance_to_box(pt2, bbox) <= self.epsilon:
                    v = node_id
                    
            if u and v and u != v:
                g.add_edge(u, v)
                
        self.validate_tnb_compliance(g)
        return g

    def validate_tnb_compliance(self, g: nx.DiGraph):
        print("[SLDTopologyResolver] Auditing electrical safety against TNB ESAG grid codes...")
        nodes_by_cat = {}
        for n, data in g.nodes(data=True):
            cat = data["category"]
            nodes_by_cat.setdefault(cat, []).append(n)
            
        # Audit 1: Check presence of Anti-Islanding protective devices
        is_islanding_relay_present = "Anti_Islanding_Relay" in nodes_by_cat
        if not is_islanding_relay_present:
            print(" [WARNING] TNB Code Violation: Anti-Islanding Protection Relay missing from schematic.")
        else:
            print(" [PASS] Anti-Islanding Protection Relay is correctly configured.")

        # Audit 2: Validate Transformer-to-Inverter connection flow
        transformers = nodes_by_cat.get("Transformer", [])
        grid_interconnections = nodes_by_cat.get("Grid_Connection", [])
        
        if transformers and grid_interconnections:
            for xfmr in transformers:
                # Confirm there is a path from Transformer to Grid Connection
                if not nx.has_path(g, xfmr, grid_interconnections[0]):
                    print(f" [VIOLATION] Disconnected Flow: No electrical path from Transformer {xfmr} to Grid Interconnection.")
                else:
                    print(" [PASS] Transformer connects safely to the TNB Grid Interconnection.")


class YieldFeasibilityEngine:
    """
    Simulates annual photovoltaic generation yields in tropical environments and models
    project lifecycle financials (LCOE, NPV, IRR) in Malaysian Ringgit.
    """
    def __init__(self, metadata: LandTitleMetadata):
        self.metadata = metadata

    def calculate(self) -> TechnicalFeasibilityModel:
        print("[YieldFeasibilityEngine] Executing financial and clean energy yield models...")
        land_sqm = self.metadata.area_sq_meters
        usable_area = land_sqm * 0.90 # 10% setback buffers
        
        # Engineering parameters for tropical environments
        gcr = 0.45 # Ground Coverage Ratio
        panel_efficiency = 0.215 # 21.5% Mono-PERC modules
        performance_ratio = 0.78 # Standard system loss index
        avg_ghi = 1550.0 # kWh/m2/year (Peninsular Malaysia solar average GHI)
        cell_temperature_derating = 0.88 # 12% loss due to high ambient operating heat
        
        # Capacity sizing: Standard utility ground footprint is approx. 3 acres (12,140 sqm) per MWp
        capacity_mwp = usable_area / 12140.0
        
        # Annual energy yield calculation
        annual_yield_mwh = capacity_mwp * 1000.0 * avg_ghi * performance_ratio * cell_temperature_derating / 1000.0
        
        # Financial input assumptions (RM)
        capex_per_mwp = 3000000.0 # RM 3.0 Million per MWp
        opex_per_mwp_year = 45000.0 # RM 45k per MWp/year
        project_lifetime = 21 # 21-year SEDA PPA NEM contract
        tariff_rm_kwh = 0.23 # average commercial NEM NOVA rate
        wacc = 0.065 # 6.5% discount rate
        
        total_capex = capacity_mwp * capex_per_mwp
        discounted_costs = total_capex
        discounted_energy = 0.0
        cash_flows = [-total_capex]
        
        # Project Cash Flow Lifecycle Simulation
        for yr in range(1, project_lifetime + 1):
            # Degradation factor: 0.5% annual loss in performance output
            degradation = (1.0 - 0.005)**(yr - 1)
            yearly_gen_kwh = annual_yield_mwh * 1000.0 * degradation
            
            # OPEX inflates at 2.0% annually
            yearly_opex = (capacity_mwp * opex_per_mwp_year) * (1.02)**(yr - 1)
            yearly_revenue = yearly_gen_kwh * tariff_rm_kwh
            yearly_net_cash = yearly_revenue - yearly_opex
            
            cash_flows.append(yearly_net_cash)
            
            discounted_costs += yearly_opex / ((1.0 + wacc)**yr)
            discounted_energy += yearly_gen_kwh / ((1.0 + wacc)**yr)
            
        # LCOE (Levelized Cost of Electricity)
        lcoe_rm_kwh = discounted_costs / discounted_energy if discounted_energy > 0 else 0.0
        
        # NPV (Net Present Value)
        npv = -total_capex
        for yr in range(1, project_lifetime + 1):
            npv += cash_flows[yr] / ((1.0 + wacc)**yr)
            
        # Newton-Raphson IRR Solver
        r = 0.10 # Initial guess of 10%
        for _ in range(100):
            f_val = sum(cf / ((1.0 + r)**t) for t, cf in enumerate(cash_flows))
            f_deriv = sum(-t * cf / ((1.0 + r)**(t + 1)) for t, cf in enumerate(cash_flows))
            if abs(f_deriv) < 1e-12:
                break
            r_new = r - f_val / f_deriv
            if abs(r_new - r) < 1e-6:
                r = r_new
                break
            r = r_new
            
        payback = total_capex / (cash_flows[1] if cash_flows[1] > 0 else 1e-12)
        
        return TechnicalFeasibilityModel(
            capacity_mwp=round(capacity_mwp, 3),
            annual_yield_mwh=round(annual_yield_mwh, 2),
            estimated_capex_rm=round(total_capex, 2),
            lcoe_rm_kwh=round(lcoe_rm_kwh, 4),
            npv_rm=round(npv, 2),
            irr_percent=round(r * 100.0, 2),
            payback_years=round(payback, 2)
        )


class FormFiller:
    """
    Maps verified legal, technical, and financial attributes into compliant,
    pre-filled regulatory filing manifests for SEDA and TNB.
    """
    @staticmethod
    def generate_manifest(land: LandTitleMetadata, tech: TechnicalFeasibilityModel) -> RegulatoryFilingManifest:
        print("[FormFiller] Generating pre-filled SEDA & TNB grid application manifest...")
        
        # Map fields to SEDA NEM-NOVA Scheme requirements
        seda = SEDAApplicationSchema(
            Part_A_Applicant_Name=land.owners[1].name, # Solarvest Development Sdn Bhd
            Part_A_Company_Registration=land.owners[1].ic_or_co_no,
            Part_B_Site_Title_Number=land.title_no,
            Part_B_Site_Lot_Number=land.lot_no,
            Part_B_Mukim_Daerah_Negeri=f"{land.mukim}, {land.district}, {land.state}",
            Part_C_Proposed_DC_Capacity_kWp=float(tech.capacity_mwp * 1000.0),
            Part_C_Proposed_AC_Capacity_kWac=float(tech.capacity_mwp * 1000.0 * 0.85), # standard DC/AC ratio
            Part_D_PPA_Tariff_Rate_RM_kWh=tech.lcoe_rm_kwh
        )
        
        # Map fields to TNB Medium Voltage Grid Connection Request
        tnb = TNBConnectionSchema(
            Applicant_Company=land.owners[1].name,
            Interconnection_Voltage_Level_kV=33.0 if tech.capacity_mwp >= 2.0 else 11.0,
            Total_Generation_Capacity_MWac=float(tech.capacity_mwp * 0.85),
            Inverter_Compliance_Standards=["IEC 62116", "IEC 61727", "MS 1837:2010"],
            Point_of_Common_Coupling=f"TNB Substation - Mukim {land.district}",
            Transformer_Capacity_MVA=float(tech.capacity_mwp * 1.2) # standard 20% electrical headroom
        )
        
        return RegulatoryFilingManifest(seda_application=seda, tnb_grid_request=tnb)


def main():
    print("=== SOLAR PROJECT INTELLIGENCE AGENT (MAIC NEXUS CHALLENGE) ===\n")
    output_dir = r"C:\Users\lewka\deep_learning\MAIC Nexus Challenge"
    
    # 1. Parse Land Title
    raw_ocr_input = """
    HAKMILIK: GRN 45293  LOT NO: Lot 8192  NEGERI: Perak
    DAERAH: Larut dan Matang  MUKIM: Mukim Asam Kumbang
    KATEGORI KEGUNAAN TANAH: Pertanian
    KELUASAN: 12 Ekar 2 Rood 15 Pole
    SYARAT-SYARAT NYATA: Tanah ini hendaklah digunakan untuk tanaman getah sahaja.
    SENARAI PEMILIK:
    1. Ahmad Bin Ismail (IC: 650212-08-5431) - Syer: 1/3
    2. Solarvest Development Sdn Bhd (Co: 1234567-U) - Syer: 2/3
    URUSNIAGA & BEBANAN:
    Kaveat Persendirian oleh Maybank Berhad dimasukkan pada 12 Jun 2021.
    """
    parser = LandTitleParser()
    land_metadata = parser.parse(raw_ocr_input)
    
    # 2. Resolve SLD Topology
    # Bounding boxes represent detected visual equipment
    symbols = [
        {"id": "PV_1", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
        {"id": "INV_1", "class": "Inverter", "bbox": [100, 400, 200, 500]},
        {"id": "RELAY_1", "class": "Anti_Islanding_Relay", "bbox": [100, 700, 200, 800]},
        {"id": "XFMR_1", "class": "Transformer", "bbox": [100, 1000, 200, 1100]},
        {"id": "GRID_1", "class": "Grid_Connection", "bbox": [100, 1300, 200, 1400]}
    ]
    # Line segments representing wiring branches
    lines = [
        ((200, 150), (400, 150)),   # PV to Inverter
        ((500, 150), (700, 150)),   # Inverter to Islanding Relay
        ((800, 150), (1000, 150)),  # Islanding Relay to Transformer
        ((1100, 150), (1300, 150))  # Transformer to Grid Connection
    ]
    resolver = SLDTopologyResolver()
    sld_graph = resolver.resolve(symbols, lines)
    
    # 3. Compute Yield and Financials
    feasibility_engine = YieldFeasibilityEngine(land_metadata)
    tech_results = feasibility_engine.calculate()
    
    # 4. Generate SEDA/TNB Prefilled Manifest
    regulatory_manifest = FormFiller.generate_manifest(land_metadata, tech_results)
    
    # Compile final execution package
    final_output = {
        "land_title_analysis": land_metadata.model_dump(),
        "sld_topology_analysis": {
            "node_count": sld_graph.number_of_nodes(),
            "edge_count": sld_graph.number_of_edges(),
            "graph_paths": list(sld_graph.edges())
        },
        "technical_financial_feasibility": tech_results.model_dump(),
        "regulatory_manifest": regulatory_manifest.model_dump()
    }
    
    # Save output report
    report_path = os.path.join(output_dir, "solar_assessment_report.json")
    with open(report_path, "w") as f:
        json.dump(final_output, f, indent=4)
        
    print(f"\n[Success] Complete Solar Assessment Report successfully written to: {report_path}")
    print(f"Calculated Capacity: {tech_results.capacity_mwp} MWp")
    print(f"Project Lifetime NPV: RM {tech_results.npv_rm:,}")
    print(f"Project IRR: {tech_results.irr_percent}%")
    print(f"Land Legal Status: {land_metadata.legal_assessment.status}")


if __name__ == "__main__":
    main()
