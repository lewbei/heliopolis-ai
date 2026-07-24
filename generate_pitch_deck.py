"""Generate a simple PDF pitch deck for Heliopolis-AI using Matplotlib."""

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parent
OUTPUT_PDF = REPO_ROOT / "pitch_deck.pdf"
SLOPE_PLOT = REPO_ROOT / "qrspi" / "plots" / "perak_slope_risk_contour.png"
SLD_PLOT = REPO_ROOT / "qrspi" / "plots" / "sld_topology_flow_graph.png"


class PitchDeck:
    def __init__(self, pdf_path: Path):
        self.pdf = PdfPages(str(pdf_path))
        self.fig_width = 16
        self.fig_height = 9
        self.colors = {
            "bg": "#0f172a",
            "title": "#f8fafc",
            "subtitle": "#cbd5e1",
            "accent": "#38bdf8",
            "text": "#e2e8f0",
            "muted": "#94a3b8",
        }

    def _new_slide(self, title: str, subtitle: Optional[str] = None):
        fig = plt.figure(figsize=(self.fig_width, self.fig_height))
        fig.patch.set_facecolor(self.colors["bg"])
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        # Top accent bar
        ax.add_patch(plt.Rectangle((0.05, 0.92), 0.9, 0.01, color=self.colors["accent"], transform=ax.transAxes))

        # Title
        ax.text(0.08, 0.86, title, fontsize=28, fontweight="bold", color=self.colors["title"], ha="left", va="top")

        if subtitle:
            ax.text(0.08, 0.78, subtitle, fontsize=16, color=self.colors["subtitle"], ha="left", va="top", style="italic")

        return fig, ax

    def _save_slide(self, fig: plt.Figure):
        self.pdf.savefig(fig, facecolor=self.colors["bg"], bbox_inches="tight")
        plt.close(fig)

    def slide_title(self):
        fig, ax = self._new_slide("")
        ax.text(0.5, 0.62, "Heliopolis-AI", fontsize=54, fontweight="bold", color=self.colors["title"], ha="center", va="center")
        ax.text(0.5, 0.50, "Solar Project Intelligence Agent", fontsize=26, color=self.colors["accent"], ha="center", va="center")
        ax.text(0.5, 0.40,
                 "Engineering-grade, neural-symbolic due diligence for LSS & C&I solar in Malaysia",
                 fontsize=16, color=self.colors["subtitle"], ha="center", va="center")
        ax.text(0.5, 0.22, "Track T1: AI for Clean Energy (Solarvest Holdings Berhad)",
                fontsize=14, color=self.colors["muted"], ha="center", va="center")
        ax.text(0.5, 0.16, "Multimedia University (MMU), Melaka, Malaysia",
                fontsize=13, color=self.colors["muted"], ha="center", va="center")
        ax.text(0.5, 0.10, "github.com/lewbei/heliopolis-ai",
                fontsize=13, color=self.colors["accent"], ha="center", va="center")
        self._save_slide(fig)

    def slide_problem(self):
        fig, ax = self._new_slide("Solar developers lose 2–6 weeks on every site intake")
        lines = [
            "• Land bottleneck: Geran scans use Ekar/Rood/Pole, fractured co-owners, hidden Caveat/Charge/Malay-Reserve flags.",
            "• Grid bottleneck: SLDs must satisfy TNB ESAG / MS 1837:2010; errors trigger expensive rejections.",
            "• Terrain risk: Satellite photos hide >15° slopes and monsoon landslide hazards.",
            "• Financial uncertainty: LSS PPA, C&I NEM, and self-consumption tariffs produce radically different NPVs.",
        ]
        y = 0.68
        for line in lines:
            ax.text(0.10, y, line, fontsize=18, color=self.colors["text"], ha="left", va="top")
            y -= 0.10
        self._save_slide(fig)

    def slide_solution(self):
        fig, ax = self._new_slide("Heliopolis-AI automates land, grid, terrain & finance")
        flow = [
            ("Scanned Deed / SLD", 0.78),
            ("Gemini Vision OCR", 0.68),
            ("Legal Parser → Civil Slope → SLD Graph → Financial Engine", 0.56),
            ("SEDA + TNB Prefilled Manifests", 0.44),
        ]
        for text, y in flow:
            ax.text(0.5, y, text, fontsize=18, color=self.colors["text"], ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor=self.colors["accent"], linewidth=1.5))
        ax.text(0.5, 0.28, "All math is deterministic — no LLM hallucination on engineering or finance.",
                fontsize=16, color=self.colors["accent"], ha="center", va="center", fontweight="bold")
        self._save_slide(fig)

    def slide_demo(self):
        fig, ax = self._new_slide("Demo output: C&I NEM / ATAP scenario")
        metrics = [
            ("Site", "Johor, 9.3 ha"),
            ("DC Capacity", "6.90 MWp"),
            ("Annual Yield", "~10,600 MWh/year"),
            ("Final CAPEX", "RM 20.7M"),
            ("NPV (21 yrs)", "RM 10.5M"),
            ("IRR", "12.38%"),
            ("Land Legal Status", "Flagged/Risky (Pertanian → NLC §124)"),
            ("BESS Required", "No (injection < 15%)"),
            ("NEMAS Required", "Yes (>72 kWac)"),
            ("Applicant", "Solarvest Development Sdn Bhd"),
        ]
        y = 0.72
        for label, value in metrics:
            ax.text(0.12, y, label, fontsize=15, color=self.colors["muted"], ha="left", va="top")
            ax.text(0.55, y, value, fontsize=15, color=self.colors["text"], ha="left", va="top", fontweight="bold")
            y -= 0.055
        self._save_slide(fig)

    def slide_modules(self):
        fig, ax = self._new_slide("Six integrated modules")
        modules = [
            "1. Legal Parser — title metadata, imperial → metric, co-owner shares",
            "2. Civil Slope Analyzer — 2D finite-difference gradients + earthworks premium",
            "3. SLD Graph Resolver — NetworkX + TNB anti-islanding/grid-path audit",
            "4. Financial Engine — tropical derating, degradation, BESS OPEX, IRR",
            "5. Scenario Selector — LSS PPA / C&I NEM / self-consumption tariffs",
            "6. Manifest Generator — SEDA & TNB prefilled forms + NEMAS checklist",
        ]
        y = 0.72
        for mod in modules:
            ax.text(0.10, y, mod, fontsize=18, color=self.colors["text"], ha="left", va="top")
            y -= 0.09
        self._save_slide(fig)

    def slide_moat(self):
        fig, ax = self._new_slide("Technical moat")
        points = [
            "• Junction-dot-aware SLD parsing — splits at real dots, ignores plain crossings",
            "• Scale-invariant ε-neighbor search — works from A4 to A0 drawings",
            "• Scenario-based finance — one model, three revenue realities",
            "• Malaysian legal domain — NLC 1965, Ekar/Rood/Pole, SEDA NEMAS",
            "• Offline core — symbolic solvers run locally; only OCR is cloud",
        ]
        y = 0.72
        for pt in points:
            ax.text(0.10, y, pt, fontsize=18, color=self.colors["text"], ha="left", va="top")
            y -= 0.10
        self._save_slide(fig)

    def slide_market(self):
        fig, ax = self._new_slide("Market & business model")
        ax.text(0.10, 0.70, "Target customers:", fontsize=20, color=self.colors["accent"], ha="left", va="top", fontweight="bold")
        targets = [
            "• Solar EPC contractors",
            "• Independent Power Producers (IPPs)",
            "• Land-search / due-diligence consultancies",
        ]
        y = 0.62
        for t in targets:
            ax.text(0.12, y, t, fontsize=17, color=self.colors["text"], ha="left", va="top")
            y -= 0.07

        ax.text(0.10, 0.38, "Go-to-market:", fontsize=20, color=self.colors["accent"], ha="left", va="top", fontweight="bold")
        gtm = [
            "1. Pilot with Solarvest Innovation Lab or regional EPC — 3–5 live sites",
            "2. B2B SaaS tiered by site-screening volume",
            "3. Enterprise API integrations for large EPCs / IPPs",
        ]
        y = 0.30
        for item in gtm:
            ax.text(0.12, y, item, fontsize=17, color=self.colors["text"], ha="left", va="top")
            y -= 0.07
        self._save_slide(fig)

    def slide_traction(self):
        fig, ax = self._new_slide("Traction & verification")
        points = [
            "[OK] 28/28 unit & integration tests passing",
            "[OK] Streamlit app passes health checks",
            "[OK] Public GitHub repo: github.com/lewbei/heliopolis-ai",
            "[OK] Complete QRSPI compliance folder",
            "[OK] Positive-NPV demo output (C&I NEM: NPV RM 10.5M, IRR 12.38%)",
            "[OK] Visual outputs: slope map + SLD graph",
        ]
        y = 0.72
        for pt in points:
            ax.text(0.10, y, pt, fontsize=18, color=self.colors["text"], ha="left", va="top")
            y -= 0.10
        self._save_slide(fig)

    def slide_visuals(self):
        fig, ax = self._new_slide("Visual proof")
        # Two image axes side by side
        if SLOPE_PLOT.exists():
            img_ax = fig.add_axes([0.08, 0.15, 0.40, 0.60])
            img_ax.imshow(Image.open(SLOPE_PLOT))
            img_ax.axis("off")
            img_ax.set_title("Terrain Slope Risk Map", color=self.colors["subtitle"], fontsize=13, pad=10)
        if SLD_PLOT.exists():
            img_ax2 = fig.add_axes([0.52, 0.15, 0.40, 0.60])
            img_ax2.imshow(Image.open(SLD_PLOT))
            img_ax2.axis("off")
            img_ax2.set_title("SLD Topology Flow Graph", color=self.colors["subtitle"], fontsize=13, pad=10)
        self._save_slide(fig)

    def slide_team(self):
        fig, ax = self._new_slide("Team")
        ax.text(0.5, 0.55, "Multimedia University (MMU), Melaka, Malaysia",
                fontsize=22, color=self.colors["text"], ha="center", va="center")
        ax.text(0.5, 0.45,
                 "Software engineering · Clean-energy domain research · Malaysian regulatory knowledge",
                 fontsize=16, color=self.colors["subtitle"], ha="center", va="center")
        ax.text(0.5, 0.35,
                 "Clean-room code built on NumPy, NetworkX, Pydantic, Matplotlib, Plotly, Streamlit, Google GenAI",
                 fontsize=14, color=self.colors["muted"], ha="center", va="center")
        self._save_slide(fig)

    def slide_ask(self):
        fig, ax = self._new_slide("What we are looking for")
        asks = [
            "1. Pilot partner — Solarvest Innovation Lab or a Malaysian EPC to validate on 3–5 live sites",
            "2. Investment / prize support — to build live e-Tanah / myTNB / SEDA integrations and hosted SaaS",
            "3. MAIC Nexus + HATI mentorship — on B2B sales and regulatory partnerships",
        ]
        y = 0.68
        for ask in asks:
            ax.text(0.10, y, ask, fontsize=18, color=self.colors["text"], ha="left", va="top")
            y -= 0.12
        ax.text(0.5, 0.28,
                 "Heliopolis-AI turns weeks of manual solar due diligence into auditable, minutes-long intelligence.",
                 fontsize=17, color=self.colors["accent"], ha="center", va="center", fontweight="bold")
        self._save_slide(fig)

    def slide_closing(self):
        fig, ax = self._new_slide("")
        ax.text(0.5, 0.58, "Thank you", fontsize=52, fontweight="bold", color=self.colors["title"], ha="center", va="center")
        ax.text(0.5, 0.44, "Heliopolis-AI  ·  Solar Project Intelligence Agent for Malaysia",
                fontsize=18, color=self.colors["subtitle"], ha="center", va="center")
        ax.text(0.5, 0.32, "github.com/lewbei/heliopolis-ai",
                fontsize=16, color=self.colors["accent"], ha="center", va="center")
        self._save_slide(fig)

    def build(self):
        self.slide_title()
        self.slide_problem()
        self.slide_solution()
        self.slide_demo()
        self.slide_modules()
        self.slide_moat()
        self.slide_market()
        self.slide_traction()
        self.slide_visuals()
        self.slide_team()
        self.slide_ask()
        self.slide_closing()
        self.pdf.close()
        print(f"[Pitch Deck] Generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    deck = PitchDeck(OUTPUT_PDF)
    deck.build()
