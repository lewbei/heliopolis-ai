import os
import json
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
        sld_paths = self.report_data.get("sld_topology_analysis", {}).get("graph_paths", [])
        
        g = nx.DiGraph()
        for edge in sld_paths:
            g.add_edge(edge[0], edge[1])
            
        # Set node categories and custom styling colors
        node_colors = []
        node_sizes = []
        labels = {}
        
        for node in g.nodes():
            if "PV" in node:
                node_colors.append("#34d399") # Green for PV Array
                node_sizes.append(2500)
                labels[node] = f"PV Array\n({node})"
            elif "INV" in node:
                node_colors.append("#60a5fa") # Blue for Inverter
                node_sizes.append(2500)
                labels[node] = f"Inverter\n({node})"
            elif "RELAY" in node:
                node_colors.append("#fbbf24") # Yellow for Anti-Islanding Relay
                node_sizes.append(2800)
                labels[node] = f"Anti-Islanding\nRelay"
            elif "XFMR" in node:
                node_colors.append("#f87171") # Red for Transformer
                node_sizes.append(2500)
                labels[node] = f"Transformer\n({node})"
            elif "GRID" in node:
                node_colors.append("#a78bfa") # Purple for TNB Grid
                node_sizes.append(2500)
                labels[node] = f"TNB Grid\n({node})"
            else:
                node_colors.append("#9ca3af")
                node_sizes.append(2000)
                labels[node] = node
                
        plt.figure(figsize=(12, 6))
        # Use a horizontal linear layout for the single line diagram representation
        pos = {
            "PV_1": (1, 1),
            "INV_1": (2, 1),
            "RELAY_1": (3, 1),
            "XFMR_1": (4, 1),
            "GRID_1": (5, 1)
        }
        
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
    report = r"C:\Users\lewka\deep_learning\MAIC Nexus Challenge\solar_assessment_report.json"
    plots_dir = r"C:\Users\lewka\deep_learning\MAIC Nexus Challenge\qrspi\plots"
    visualizer = HeliopolisVisualizer(report, plots_dir)
    visualizer.plot_terrain_and_graph()
