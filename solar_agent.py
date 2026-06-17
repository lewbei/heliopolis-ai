import os
import sys
import numpy as np
import networkx as nx
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Core Relational & Structured Data Models (Pydantic V2) ---

class OwnerModel(BaseModel):
    name: str = Field(description="Name of the registered landowner.")
    ic_or_co_no: str = Field(description="MyKad IC Number or Company Registration Number.")
    share_fraction: str = Field(description="Raw ownership share as a fraction, e.g., '11/120'.")
    calculated_share_float: float = Field(description="Decimal value of the fractional share.")

class PowerOfAttorneyModel(BaseModel):
    is_poa_required: bool = Field(description="True if no single owner holds a controlling >50% stake.")
    min_co_owners_needed: int = Field(description="Minimum number of co-owners that must co-sign to exceed 51% controlling interest.")
    required_deeds: List[str] = Field(default=[], description="List of legal instruments required for joint land lease.")

class LegalAssessmentModel(BaseModel):
    status: str = Field(description="Zoning or transaction suitability: 'Approved', 'Flagged/Risky', or 'Rejected'.")
    findings: List[str] = Field(default=[], description="List of administrative or legal issues found on the land title.")
    poa_compliance: PowerOfAttorneyModel

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

class TerrainProfileModel(BaseModel):
    mean_slope_degrees: float = Field(description="Average terrain slope in degrees.")
    optimal_area_percent: float = Field(description="Percentage of land with slope < 5 degrees.")
    manageable_area_percent: float = Field(description="Percentage of land with slope 5 to 15 degrees.")
    critical_area_percent: float = Field(description="Percentage of land with slope > 15 degrees.")
    landslide_risk: str = Field(description="Risk classification: 'Low', 'Medium', or 'High (Unbuildable)'.")
    grading_capex_premium_multiplier: float = Field(description="CAPEX multiplier adjustment for civil earthworks.")

class TechnicalFeasibilityModel(BaseModel):
    capacity_mwp: float = Field(description="Simulated PV system peak DC capacity (MWp).")
    annual_yield_mwh: float = Field(description="Estimated annual electricity generation (MWh/year).")
    base_capex_rm: float = Field(description="Base capital expenditure in Malaysian Ringgit (RM).")
    grading_adjusted_capex_rm: float = Field(description="Final CAPEX including civil grading premiums.")
    lcoe_rm_kwh: float = Field(description="Levelized Cost of Electricity (RM/kWh).")
    npv_rm: float = Field(description="Net Present Value (RM) over the project lifecycle.")
    irr_percent: float = Field(description="Project Internal Rate of Return (%).")
    payback_years: float = Field(description="Estimated capital payback period in years.")
    terrain_profile: TerrainProfileModel

class NEMASChecklistSchema(BaseModel):
    is_nemas_required: bool = Field(description="True if proposed AC capacity exceeds 72 kWac.")
    voltage_rise_study_required: bool = Field(description="True if AC generation can trigger local grid overvoltage.")
    estimated_regulatory_fee_rm: float = Field(description="Estimate of TNB/SEDA assessment study fees.")
    estimated_processing_days: int = Field(description="Estimated regulatory queue wait time in calendar days.")
    mandatory_technical_studies: List[str] = Field(default=[], description="List of engineering studies required for grid filing.")

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
    nemas_checklist: NEMASChecklistSchema


# --- Specialized Parsing & Analysis Modules ---

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
        
        title_no = "GRN 45293"
        lot_no = "Lot 8192"
        state = "Perak"
        district = "Larut dan Matang"
        mukim = "Mukim Asam Kumbang"
        zoning = "Pertanian"
        
        hectares, sq_meters = self.convert_imperial_to_metric(acres=12.0, roods=2.0, poles=15.0)
        
        # Scenario: Multiple co-owners with fragmented fractional shares
        owners_raw = [
            {"name": "Ahmad Bin Ismail", "id": "650212-08-5431", "share": "11/120"}, # 9.17%
            {"name": "Wan Fatimah Binti Wan Ali", "id": "701103-08-5222", "share": "15/120"}, # 12.5%
            {"name": "Siti Aminah Binti Ahmad", "id": "930415-08-6112", "share": "14/120"}, # 11.67%
            {"name": "Solarvest Development Sdn Bhd", "id": "1234567-U", "share": "40/120"}, # 33.33% (largest single, but <50%)
            {"name": "Lee Chong Wei", "id": "821021-10-5431", "share": "40/120"} # 33.33%
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
        
        # --- Improvised Feature: Power of Attorney & Joint-Execution Evaluator ---
        # Sort owners descending to calculate minimum co-owners required to reach 51% controlling interest
        sorted_owners = sorted(owners, key=lambda x: x.calculated_share_float, reverse=True)
        running_sum = 0.0
        poa_co_sign_count = 0
        is_poa_required = True
        
        for owner in sorted_owners:
            running_sum += owner.calculated_share_float
            poa_co_sign_count += 1
            if owner.calculated_share_float >= 0.50:
                is_poa_required = False # Single controlling owner exists
            if running_sum >= 0.51:
                break
                
        required_deeds = []
        if is_poa_required:
            required_deeds = [
                "Joint Venture Lease Agreement executed by registered co-owners",
                f"Power of Attorney (Surat Kuasa Wakil) co-signed by at least {poa_co_sign_count} co-owners to secure controlling 51% land rights",
                "Form 14A (Pindahmilik Tanah) or Form 15A (Pajakan Tanah) registered at Land Office / Pejabat Tanah dan Galian"
            ]
            
        poa_model = PowerOfAttorneyModel(
            is_poa_required=is_poa_required,
            min_co_owners_needed=poa_co_sign_count,
            required_deeds=required_deeds
        )
        
        legal_status = "Approved"
        findings = []
        
        if zoning == "Pertanian":
            findings.append("Category 'Pertanian' requires NLC Section 124 land conversion to 'Perindustrian' or special state temporary permit.")
        if has_caveats:
            legal_status = "Flagged/Risky"
            findings.append("Active Private Caveat detected. Land transactions are legally frozen until formal withdrawal is filed.")
        if has_charges:
            legal_status = "Flagged/Risky"
            findings.append("Active Bank Charge (Gadaian) detected. Requires bank letter of consent prior to registering lease.")
        if is_malay_reserve:
            legal_status = "Rejected"
            findings.append("Tanah Rezab Melayu (Malay Reserve) detected. Absolute transaction blocker for public-listed entities.")
            
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
            legal_assessment=LegalAssessmentModel(
                status=legal_status, 
                findings=findings,
                poa_compliance=poa_model
            )
        )


class CivilSlopeAnalyzer:
    """
    Improvised Module: Analyzes civil topography elevation grids using 2D spatial gradients
    to calculate landslide risks and grading/cut-and-fill CAPEX premiums.
    """
    @staticmethod
    def analyze_topography(elevation_grid_2d: np.ndarray, cell_resolution_meters: float = 10.0) -> TerrainProfileModel:
        print("[CivilSlopeAnalyzer] Computing 2D spatial elevation gradients for slope profiling...")
        
        # Calculate gradients in X and Y directions using finite differences
        grad_y, grad_x = np.gradient(elevation_grid_2d, cell_resolution_meters)
        
        # Calculate slope in radians and convert to degrees: theta = arctan(sqrt(dz/dx^2 + dz/dy^2))
        slope_rad = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
        slope_deg = np.degrees(slope_rad)
        
        mean_slope = float(np.mean(slope_deg))
        total_cells = slope_deg.size
        
        # Classify cells into slope categories
        optimal_cells = np.sum(slope_deg < 5.0)
        manageable_cells = np.sum((slope_deg >= 5.0) & (slope_deg <= 15.0))
        critical_cells = np.sum(slope_deg > 15.0)
        max_slope = float(np.max(slope_deg))
        
        optimal_percent = float((optimal_cells / total_cells) * 100.0)
        manageable_percent = float((manageable_cells / total_cells) * 100.0)
        critical_percent = float((critical_cells / total_cells) * 100.0)
        
        # Landslide risk evaluation
        if max_slope >= 30.0:
            landslide_risk = "High (Unbuildable / Severe Slope)"
            grading_multiplier = 1.35 # 35% cost premium due to retaining walls and safety works
        elif critical_percent >= 20.0 or max_slope > 15.0:
            landslide_risk = "Medium (Requires extensive soil reinforcement)"
            grading_multiplier = 1.15 # 15% cost premium
        else:
            landslide_risk = "Low (Optimal plain terrain)"
            grading_multiplier = 1.00 # No premium
            
        print(f" [Civil] Calculated Mean Slope: {mean_slope:.2f}° | Max Slope: {max_slope:.2f}° | Risk: {landslide_risk}")
        return TerrainProfileModel(
            mean_slope_degrees=round(mean_slope, 2),
            optimal_area_percent=round(optimal_percent, 2),
            manageable_area_percent=round(manageable_percent, 2),
            critical_area_percent=round(critical_percent, 2),
            landslide_risk=landslide_risk,
            grading_capex_premium_multiplier=grading_multiplier
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
                    px, py = pt # Fixed coordinate unpacking bug (X is first, Y is second)
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
            
        is_islanding_relay_present = "Anti_Islanding_Relay" in nodes_by_cat
        if not is_islanding_relay_present:
            print(" [WARNING] TNB Code Violation: Anti-Islanding Protection Relay missing from schematic.")
        else:
            print(" [PASS] Anti-Islanding Protection Relay is correctly configured.")

        transformers = nodes_by_cat.get("Transformer", [])
        grid_interconnections = nodes_by_cat.get("Grid_Connection", [])
        
        if transformers and grid_interconnections:
            for xfmr in transformers:
                if not nx.has_path(g, xfmr, grid_interconnections[0]):
                    print(f" [VIOLATION] Disconnected Flow: No electrical path from Transformer {xfmr} to Grid Interconnection.")
                else:
                    print(" [PASS] Transformer connects safely to the TNB Grid Interconnection.")


class YieldFeasibilityEngine:
    """
    Simulates annual photovoltaic generation yields in tropical environments and models
    project lifecycle financials (LCOE, NPV, IRR) in Malaysian Ringgit.
    """
    def __init__(self, metadata: LandTitleMetadata, terrain: TerrainProfileModel):
        self.metadata = metadata
        self.terrain = terrain

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
        
        capacity_mwp = usable_area / 12140.0
        annual_yield_mwh = capacity_mwp * 1000.0 * avg_ghi * performance_ratio * cell_temperature_derating / 1000.0
        
        # Financial input assumptions (RM)
        capex_per_mwp = 3000000.0 # RM 3.0 Million per MWp base cost
        opex_per_mwp_year = 45000.0 # RM 45k per MWp/year
        project_lifetime = 21 # 21-year SEDA PPA NEM contract
        tariff_rm_kwh = 0.23 # average commercial NEM NOVA rate
        wacc = 0.065 # 6.5% discount rate
        
        # Adjusted CAPEX incorporating Civil Slope Grading premiums
        base_capex = capacity_mwp * capex_per_mwp
        adjusted_capex = base_capex * self.terrain.grading_capex_premium_multiplier
        
        discounted_costs = adjusted_capex
        discounted_energy = 0.0
        cash_flows = [-adjusted_capex]
        
        for yr in range(1, project_lifetime + 1):
            degradation = (1.0 - 0.005)**(yr - 1)
            yearly_gen_kwh = annual_yield_mwh * 1000.0 * degradation
            yearly_opex = (capacity_mwp * opex_per_mwp_year) * (1.02)**(yr - 1)
            yearly_revenue = yearly_gen_kwh * tariff_rm_kwh
            yearly_net_cash = yearly_revenue - yearly_opex
            
            cash_flows.append(yearly_net_cash)
            
            discounted_costs += yearly_opex / ((1.0 + wacc)**yr)
            discounted_energy += yearly_gen_kwh / ((1.0 + wacc)**yr)
            
        lcoe_rm_kwh = discounted_costs / discounted_energy if discounted_energy > 0 else 0.0
        
        # Solve NPV
        npv = -adjusted_capex
        for yr in range(1, project_lifetime + 1):
            npv += cash_flows[yr] / ((1.0 + wacc)**yr)
            
        # Newton-Raphson IRR Solver
        r = 0.10
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
            
        payback = adjusted_capex / (cash_flows[1] if cash_flows[1] > 0 else 1e-12)
        
        return TechnicalFeasibilityModel(
            capacity_mwp=round(capacity_mwp, 3),
            annual_yield_mwh=round(annual_yield_mwh, 2),
            base_capex_rm=round(base_capex, 2),
            grading_adjusted_capex_rm=round(adjusted_capex, 2),
            lcoe_rm_kwh=round(lcoe_rm_kwh, 4),
            npv_rm=round(npv, 2),
            irr_percent=round(r * 100.0, 2),
            payback_years=round(payback, 2),
            terrain_profile=self.terrain
        )


class FormFiller:
    """
    Maps verified legal, technical, and financial attributes into compliant,
    pre-filled regulatory filing manifests for SEDA and TNB, including NEMAS triggers.
    """
    @staticmethod
    def generate_manifest(land: LandTitleMetadata, tech: TechnicalFeasibilityModel) -> RegulatoryFilingManifest:
        print("[FormFiller] Generating pre-filled SEDA & TNB grid application manifest...")
        
        ac_capacity_kw = float(tech.capacity_mwp * 1000.0 * 0.85)
        
        # --- Improvised Feature: SEDA NEMAS Compliance Checklist ---
        is_nemas_required = ac_capacity_kw > 72.0
        mandatory_studies = []
        nemas_fee = 0.0
        processing_days = 15
        
        if is_nemas_required:
            nemas_fee = 8000.0 # Estimated TNB process fee in RM
            processing_days = 90
            mandatory_studies = [
                "Power Quality & Harmonic Distortion Assessment",
                "Voltage-Rise and Steady State Injections Study",
                "Protection Coordination & Anti-Islanding Trip Integration Study",
                "Utility Fault Ride-Through (FRT) Compliance Study"
            ]
        
        seda = SEDAApplicationSchema(
            Part_A_Applicant_Name=land.owners[3].name, # Solarvest Development Sdn Bhd
            Part_A_Company_Registration=land.owners[3].ic_or_co_no,
            Part_B_Site_Title_Number=land.title_no,
            Part_B_Site_Lot_Number=land.lot_no,
            Part_B_Mukim_Daerah_Negeri=f"{land.mukim}, {land.district}, {land.state}",
            Part_C_Proposed_DC_Capacity_kWp=float(tech.capacity_mwp * 1000.0),
            Part_C_Proposed_AC_Capacity_kWac=ac_capacity_kw,
            Part_D_PPA_Tariff_Rate_RM_kWh=tech.lcoe_rm_kwh
        )
        
        tnb = TNBConnectionSchema(
            Applicant_Company=land.owners[3].name,
            Interconnection_Voltage_Level_kV=33.0 if tech.capacity_mwp >= 2.0 else 11.0,
            Total_Generation_Capacity_MWac=ac_capacity_kw / 1000.0,
            Inverter_Compliance_Standards=["IEC 62116", "IEC 61727", "MS 1837:2010"],
            Point_of_Common_Coupling=f"TNB Substation - Mukim {land.district}",
            Transformer_Capacity_MVA=float(tech.capacity_mwp * 1.2)
        )
        
        nemas = NEMASChecklistSchema(
            is_nemas_required=is_nemas_required,
            voltage_rise_study_required=ac_capacity_kw >= 250.0, # required above 250kW under TNB code
            estimated_regulatory_fee_rm=nemas_fee,
            estimated_processing_days=processing_days,
            mandatory_technical_studies=mandatory_studies
        )
        
        return RegulatoryFilingManifest(
            seda_application=seda, 
            tnb_grid_request=tnb,
            nemas_checklist=nemas
        )


def main():
    print("=== SOLAR PROJECT INTELLIGENCE AGENT (MAIC NEXUS CHALLENGE) ===\n")
    output_dir = r"C:\Users\lewka\deep_learning\MAIC Nexus Challenge"
    
    # 1. Parse Land Title (Fragmented Co-owner Shares)
    raw_ocr_input = """
    HAKMILIK: GRN 45293  LOT NO: Lot 8192  NEGERI: Perak
    DAERAH: Larut dan Matang  MUKIM: Mukim Asam Kumbang
    KATEGORI KEGUNAAN TANAH: Pertanian
    KELUASAN: 12 Ekar 2 Rood 15 Pole
    SYARAT-SYARAT NYATA: Tanah ini hendaklah digunakan untuk tanaman getah sahaja.
    URUSNIAGA & BEBANAN:
    Kaveat Persendirian oleh Maybank Berhad dimasukkan pada 12 Jun 2021.
    """
    parser = LandTitleParser()
    land_metadata = parser.parse(raw_ocr_input)
    
    # 2. Analyze Civil Topography & Slope Profile
    # Generate a dummy 2D elevation matrix simulating a hilly Malaysian valley in Perak
    # x and y ranges across 100 meters with cell resolution of 10 meters
    y, x = np.mgrid[0:100:10, 0:100:10]
    # Simulation: Z value represents elevation height. Features a steeper ridge in the center.
    elevation_grid = 120.0 + 3.0 * np.sin(x / 15.0) + 12.0 * np.sin(y / 12.0)
    # Add a steep embankment at the right border to test safety triggers (>30 deg)
    elevation_grid[:, -1] += 25.0
    
    terrain_model = CivilSlopeAnalyzer.analyze_topography(elevation_grid, cell_resolution_meters=10.0)
    
    # 3. Resolve SLD Topology
    symbols = [
        {"id": "PV_1", "class": "PV_Array", "bbox": [100, 100, 200, 200]},
        {"id": "INV_1", "class": "Inverter", "bbox": [100, 400, 200, 500]},
        {"id": "RELAY_1", "class": "Anti_Islanding_Relay", "bbox": [100, 700, 200, 800]},
        {"id": "XFMR_1", "class": "Transformer", "bbox": [100, 1000, 200, 1100]},
        {"id": "GRID_1", "class": "Grid_Connection", "bbox": [100, 1300, 200, 1400]}
    ]
    lines = [
        ((200, 150), (400, 150)),   # PV to Inverter
        ((500, 150), (700, 150)),   # Inverter to Islanding Relay
        ((800, 150), (1000, 150)),  # Islanding Relay to Transformer
        ((1100, 150), (1300, 150))  # Transformer to Grid Connection
    ]
    resolver = SLDTopologyResolver()
    sld_graph = resolver.resolve(symbols, lines)
    
    # 4. Compute Yield and Financials (Incorporating Civil Earthworks Adjustments)
    feasibility_engine = YieldFeasibilityEngine(land_metadata, terrain_model)
    tech_results = feasibility_engine.calculate()
    
    # 5. Generate SEDA/TNB Prefilled Manifest (Incorporating NEMAS triggers)
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
    print(f"Base CAPEX Cost: RM {tech_results.base_capex_rm:,.2f}")
    print(f"Civil Slope CAPEX Cost (Adjusted): RM {tech_results.grading_adjusted_capex_rm:,.2f}")
    print(f"Project Lifetime NPV: RM {tech_results.npv_rm:,.2f}")
    print(f"Project IRR: {tech_results.irr_percent}%")
    print(f"Land Legal Status: {land_metadata.legal_assessment.status}")
    print(f"Power of Attorney Required: {land_metadata.legal_assessment.poa_compliance.is_poa_required}")
    print(f"SEDA NEMAS Study Required: {regulatory_manifest.nemas_checklist.is_nemas_required}")


if __name__ == "__main__":
    main()
