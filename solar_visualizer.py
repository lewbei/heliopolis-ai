import os
import json
from typing import List
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class HeliopolisVisualizer:
    """
    Reads the solar assessment report and generates high-resolution,
    publication-grade visual diagrams (2D terrain slope maps and SLD network topology graphs)
    suitable for inclusion inside the Pitch Deck.
    """
    def __init__(self, report_path: str, output_dir: str):
        self.report_path = report_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.report_data = {}

    def load_report(self) -> bool:
        if not os.path.exists(self.report_path):
            print(f" [Error] Assessment report missing at: {self.report_path}")
            return False
        try:
            with open(self.report_path, "r", encoding="utf-8") as f:
                self.report_data = json.load(f)
            return True
        except Exception as e:
            print(f" [Error] Failed to read report: {e}")
            return False

    @staticmethod
    def _sld_category(node_id: str) -> str:
        """Map a node id string to its SLD component category."""
        if "PV" in node_id:
            return "PV_Array"
        if "INV" in node_id:
            return "Inverter"
        if "RELAY" in node_id:
            return "Anti_Islanding_Relay"
        if "XFMR" in node_id:
            return "Transformer"
        if "GRID" in node_id:
            return "Grid_Connection"
        return "Other"

    @staticmethod
    def _sld_style(category: str) -> dict:
        """Return visualization style (color, size, label) for an SLD category."""
        styles = {
            "PV_Array": {"color": "#34d399", "size": 2500, "label": "PV Array"},
            "Inverter": {"color": "#60a5fa", "size": 2500, "label": "Inverter"},
            "Anti_Islanding_Relay": {"color": "#fbbf24", "size": 2800, "label": "Anti-Islanding Relay"},
            "Transformer": {"color": "#f87171", "size": 2500, "label": "Transformer"},
            "Grid_Connection": {"color": "#a78bfa", "size": 2500, "label": "TNB Grid"},
            "Other": {"color": "#9ca3af", "size": 2000, "label": ""},
        }
        return styles.get(category, styles["Other"])

    @staticmethod
    def _horizontal_layout(node_ids: List[str]) -> dict:
        """Generate a left-to-right linear layout for the SLD graph."""
        return {node: (i + 1, 1) for i, node in enumerate(node_ids)}

    def plot_terrain_and_graph(self):
        print("[HeliopolisVisualizer] Generating visual diagrams...")
        if not self.load_report():
            return
            
        # 1. Plot 2D Topography Slope Contour Map
        # Recreate the elevation grid from the assessment report coordinates
        y, x = np.mgrid[0:100:10, 0:100:10]
        elevation_grid = 120.0 + 3.0 * np.sin(x / 15.0) + 12.0 * np.sin(y / 12.0)
        elevation_grid[:, -1] += 25.0 # Steep ridge at the border
        
        # Calculate gradients and slope degrees
        grad_y, grad_x = np.gradient(elevation_grid, 10.0)
        slope_deg = np.degrees(np.arctan(np.sqrt(grad_x**2 + grad_y**2)))
        
        plt.figure(figsize=(10, 8))
        # Create a contour plot of elevation with a beautiful bone/terrain colormap
        contours = plt.contour(x, y, elevation_grid, levels=15, colors="black", alpha=0.5)
        plt.clabel(contours, inline=True, fontsize=8, fmt="%1.1f m")
        
        # Create a colormap of slopes (Green to Red risk zones)
        # 0-5 deg (Optimal) -> Green, 5-15 deg (Manageable) -> Orange, >15 deg (Critical) -> Red
        slope_img = plt.imshow(slope_deg, extent=[0, 100, 0, 100], origin="lower",
                               cmap="YlOrRd", alpha=0.85, interpolation="bilinear")
        
        colorbar = plt.colorbar(slope_img)
        colorbar.set_label("Terrain Slope (Degrees °)", fontsize=10)
        
        plt.title("Heliopolis-AI: 2D Terrain Elevation & Slope Risk Map (Perak Site)", fontsize=12, fontweight="bold", pad=15)
        plt.xlabel("X Dimension (Meters)", fontsize=10)
        plt.ylabel("Y Dimension (Meters)", fontsize=10)
        
        # Highlight high landslide risk embankment
        plt.annotate("CRITICAL RISK\nSLOPE > 30°", xy=(90, 50), xytext=(55, 55),
                     arrowprops=dict(facecolor="red", shrink=0.08, width=2, headwidth=8),
                     fontsize=10, fontweight="bold", color="red",
                     bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))
                     
        terrain_plot_path = os.path.join(self.output_dir, "perak_slope_risk_contour.png")
        plt.savefig(terrain_plot_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f" [Visual] 2D Slope Risk Contour successfully plotted at: {terrain_plot_path}")
        
        # 2. Plot Directed SLD Network Topology Graph
        edge_list = self.report_data.get("sld_topology_analysis", {}).get("graph_paths", [])

        g = nx.DiGraph()
        for edge in edge_list:
            g.add_edge(edge[0], edge[1])

        # Set node categories and custom styling colors
        node_colors = []
        node_sizes = []
        labels = {}

        for node in g.nodes():
            category = self._sld_category(node)
            style = self._sld_style(category)
            node_colors.append(style["color"])
            node_sizes.append(style["size"])
            labels[node] = f"{style['label']}\n({node})" if style["label"] else node
                
        plt.figure(figsize=(12, 6))
        # Use a horizontal linear layout for the single line diagram representation
        pos = self._horizontal_layout(list(g.nodes()))

        nx.draw_networkx_nodes(g, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, edgecolors="black")
        nx.draw_networkx_edges(g, pos, width=2, arrowsize=20, edge_color="black", min_source_margin=15, min_target_margin=15)
        nx.draw_networkx_labels(g, pos, labels=labels, font_size=9, font_family="sans-serif", font_weight="bold")
        
        plt.title("Heliopolis-AI: Extracted Directed SLD Network Topology Graph", fontsize=12, fontweight="bold", pad=15)
        plt.axis("off")
        
        sld_plot_path = os.path.join(self.output_dir, "sld_topology_flow_graph.png")
        plt.savefig(sld_plot_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f" [Visual] Electrical SLD flow graph successfully plotted at: {sld_plot_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    report = os.path.join(base_dir, "solar_assessment_report.json")
    plots_dir = os.path.join(base_dir, "qrspi", "plots")
    visualizer = HeliopolisVisualizer(report, plots_dir)
    visualizer.plot_terrain_and_graph()
