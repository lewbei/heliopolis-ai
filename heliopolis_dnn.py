import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# --- Custom Modern Activation Function: SwiGLU ---

class SwiGLU(nn.Module):
    """
    Swish-Gated Linear Unit (SwiGLU) activation function,
    widely utilized in state-of-the-art transformer and reasoning architectures.
    """
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.w = nn.Linear(in_features, out_features)
        self.v = nn.Linear(in_features, out_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Swish(x) = x * sigmoid(x)
        swish_gate = self.w(x) * torch.sigmoid(self.w(x))
        return swish_gate * self.v(x)


# --- Custom Multi-Head Neural Network Architecture ---

class HeliopolisDNN(nn.Module):
    """
    Custom PyTorch Multi-Head Deep Neural Network for Solar Project Assessment.
    Takes physical, topographic, and transactional land features and simultaneously predicts:
    1. Site Feasibility Probability (Classification Head)
    2. Optimized Levelized Cost of Electricity (LCOE) (Regression Head)
    """
    def __init__(self, input_dim: int = 6, hidden_dim: int = 64):
        super().__init__()
        
        # Shared representations with SwiGLU gates and Dropout regularization
        self.shared_layer1 = SwiGLU(input_dim, hidden_dim)
        self.dropout1 = nn.Dropout(0.1)
        self.shared_layer2 = SwiGLU(hidden_dim, hidden_dim)
        self.dropout2 = nn.Dropout(0.1)
        
        # Head 1: Binary Classification (Feasibility Success Probability)
        self.classifier_head = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid() # Restricts output range to [0, 1]
        )
        
        # Head 2: Continuous Regression (Optimized LCOE in RM/kWh)
        self.regressor_head = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1) # Continuous value output
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # Process shared representations
        h = self.shared_layer1(x)
        h = self.dropout1(h)
        h = self.shared_layer2(h)
        h = self.dropout2(h)
        
        # Get head-specific predictions
        feasibility_prob = self.classifier_head(h)
        predicted_lcoe = self.regressor_head(h)
        
        return feasibility_prob, predicted_lcoe


# --- Dataset Generation & Training Pipeline ---

def load_real_grounded_malaysian_solar_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Loads 100% physically and legally grounded site registry data for Malaysia
    and simulates tropical clean-energy yields and legal transaction barriers
    to formulate the model's true multi-task training distributions.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    registry_path = os.path.join(base_dir, "real_malaysian_sites_registry.json")
    
    if not os.path.exists(registry_path):
        raise FileNotFoundError(f"Real site registry not found at: {registry_path}")
        
    with open(registry_path, "r", encoding="utf-8") as f:
        registry_data = json.load(f)
        
    print(f"[Data Loader] Loading {len(registry_data)} real grounded Malaysian site records...")
    
    features = []
    feasibility = []
    lcoes = []
    
    for item in registry_data:
        area = float(item["area_sq_meters"])
        mean_slope = float(item["mean_slope_degrees"])
        max_slope = float(item["max_slope_degrees"])
        grid_dist = float(item["grid_proximity_km"])
        owners_count = float(item["co_owners_count"])
        ghi = float(item["annual_ghi_kwh_m2_year"])
        temp_max = float(item["avg_temp_max_c"])
        
        is_malay_reserve = item["is_malay_reserve"]
        has_caveats = item["has_caveats"]
        has_charges = item["has_charges"]
        
        # 6-dimensional input vector: Area, Mean Slope, Max Slope, Grid Proximity, Co-owners, GHI
        feat_vector = [area, mean_slope, max_slope, grid_dist, owners_count, ghi]
        features.append(feat_vector)
        
        # Feasibility classification: site must be physically buildable (mean slope < 15),
        # close to grid (< 6.0 km), manageable legal status (owners count < 5),
        # and free from absolute transaction blocks like Malay Reserve Land, caveats, or charges.
        is_feasible = 1.0 if (
            mean_slope < 15.0 and 
            grid_dist < 6.0 and 
            owners_count < 5.0 and 
            not is_malay_reserve and 
            not has_caveats and 
            not has_charges
        ) else 0.0
        feasibility.append(is_feasible)
        
        # Physical Clean-Energy yield and financial LCOE simulation
        usable_area = area * 0.90
        capacity_mwp = usable_area / 12140.0
        
        # Tropical cell temperature derating
        t_cell_estimated = temp_max + 20.0
        temp_coeff = -0.0035
        cell_temperature_derating = max(0.70, min(1.0, 1.0 + (t_cell_estimated - 25.0) * temp_coeff))
        
        performance_ratio = 0.78
        annual_yield_mwh = capacity_mwp * 1000.0 * ghi * performance_ratio * cell_temperature_derating / 1000.0
        
        # Costs
        capex_per_mwp = 3000000.0
        opex_per_mwp_year = 45000.0
        project_lifetime = 21
        wacc = 0.065
        
        # Civil slope earthwork grading multiplier
        if max_slope >= 30.0:
            grading_multiplier = 1.35
        elif max_slope > 15.0:
            grading_multiplier = 1.15
        else:
            grading_multiplier = 1.00
            
        # Grid battery storage (BESS) sizing
        ac_capacity = capacity_mwp * 0.85
        substation_mva = float(item["substation_capacity_mva"])
        injection_percent = (ac_capacity / substation_mva) * 100.0
        
        bess_capex = 0.0
        bess_opex = 0.0
        if injection_percent > 15.0:
            excess_mw = ac_capacity - (0.15 * substation_mva)
            bess_power = excess_mw
            bess_energy = bess_power * 4.0
            bess_capex = (bess_power * 1200000.0) + (bess_energy * 1000000.0)
            bess_opex = bess_capex * 0.015
            
        adjusted_capex = (capacity_mwp * capex_per_mwp * grading_multiplier) + bess_capex
        
        discounted_costs = adjusted_capex
        discounted_energy = 0.0
        
        for yr in range(1, project_lifetime + 1):
            degradation = (1.0 - 0.005)**(yr - 1)
            yearly_gen_kwh = annual_yield_mwh * 1000.0 * degradation
            yearly_opex = (capacity_mwp * opex_per_mwp_year + bess_opex) * (1.02)**(yr - 1)
            
            discounted_costs += yearly_opex / ((1.0 + wacc)**yr)
            discounted_energy += yearly_gen_kwh / ((1.0 + wacc)**yr)
            
        lcoe = discounted_costs / (discounted_energy + 1e-12) if discounted_energy > 0 else 0.0
        lcoes.append(lcoe)
        
    X = np.array(features, dtype=np.float32)
    y_class = np.array(feasibility, dtype=np.float32).reshape(-1, 1)
    y_reg = np.array(lcoes, dtype=np.float32).reshape(-1, 1)
    
    # Clip extreme LCOE outliers for model training stability
    y_reg = np.clip(y_reg, 0.15, 0.85)
    
    # Normalize features using z-score
    X_mean = np.mean(X, axis=0)
    X_std = np.std(X, axis=0) + 1e-12
    X_normalized = (X - X_mean) / X_std
    
    # Save normalization constants
    norm_constants = {"mean": X_mean.tolist(), "std": X_std.tolist()}
    norm_dest = os.path.join(base_dir, "normalization_constants.json")
    with open(norm_dest, "w") as f:
        json.dump(norm_constants, f, indent=4)
        
    print(f"[Success] Processed real-world features and saved normalization constants to: {norm_dest}")
    return X_normalized, y_class, y_reg


def train_model():
    print("=== HELIOPOLIS-AI DEEP LEARNING TRAINING PIPELINE ===\n")
    models_dir = r"C:\Users\lewka\deep_learning\MAIC Nexus Challenge\models"
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Load real-world grounded training data
    X, y_class, y_reg = load_real_grounded_malaysian_solar_data()
    
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_class_tensor = torch.tensor(y_class, dtype=torch.float32)
    y_reg_tensor = torch.tensor(y_reg, dtype=torch.float32)
    
    # 2. Instantiate our multi-head network
    model = HeliopolisDNN(input_dim=6, hidden_dim=64)
    
    # 3. Define multi-task loss functions and optimizer
    bce_loss_fn = nn.BCELoss() # Binary Cross Entropy for classification
    mse_loss_fn = nn.MSELoss() # Mean Squared Error for regression
    optimizer = optim.AdamW(model.parameters(), lr=0.005, weight_decay=1e-4)
    
    epochs = 150
    print(f"[Training] Initiating training loop for {epochs} epochs...")
    
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()
        
        # Forward pass through our shared-representation networks
        pred_class, pred_reg = model(X_tensor)
        
        # Compute joint multi-task loss
        loss_class = bce_loss_fn(pred_class, y_class_tensor)
        loss_reg = mse_loss_fn(pred_reg, y_reg_tensor)
        joint_loss = loss_class + 10.0 * loss_reg # scale reg loss to align magnitudes
        
        # Backward pass & weight updates
        joint_loss.backward()
        optimizer.step()
        
        if epoch % 25 == 0 or epoch == 1:
            print(f"  Epoch {epoch:03d}/{epochs:03d} | Joint Loss: {joint_loss.item():.4f} | Class Loss: {loss_class.item():.4f} | Reg Loss: {loss_reg.item():.4f}")
            
    # 4. Save Trained Model weights atomically (Blindspot protected)
    model_weight_path = os.path.join(models_dir, "heliopolis_dnn.pt")
    tmp_weight_path = model_weight_path + ".tmp"
    
    try:
        torch.save(model.state_dict(), tmp_weight_path)
        os.replace(tmp_weight_path, model_weight_path)
        print(f"\n[Success] Trained HeliopolisDNN weights successfully saved to: {model_weight_path}")
    except Exception as e:
        if os.path.exists(tmp_weight_path):
            os.remove(tmp_weight_path)
        print(f" [ERROR] Saving model weights failed: {e}")
        sys.exit(1)
        
    # 5. Run local model inference on our Perak Site
    # Features of Perak site: Area=50,965 sqm, Mean Slope=37.76°, Max Slope=70.38°, Grid Dist=2.5km, Owners=5, GHI=1550
    raw_perak_features = np.array([[50965.0, 37.76, 70.38, 2.5, 5.0, 1550.0]])
    
    # Load normalization constants
    with open(r"C:\Users\lewka\deep_learning\MAIC Nexus Challenge\normalization_constants.json", "r") as f:
        norm = json.load(f)
    mean = np.array(norm["mean"])
    std = np.array(norm["std"])
    
    perak_norm = (raw_perak_features - mean) / std
    perak_tensor = torch.tensor(perak_norm, dtype=torch.float32)
    
    model.eval()
    with torch.no_grad():
        pred_feasibility, pred_lcoe_val = model(perak_tensor)
        
    print("\n=== HELIOPOLIS-AI MODEL INFERENCE PREDICTIONS (PERAK SITE) ===")
    print(f"  Predicted Feasibility Success Probability: {pred_feasibility.item() * 100.0:.2f}%")
    print(f"  Predicted Levelized Cost of Electricity: RM {pred_lcoe_val.item():.4f} / kWh")
    print("===============================================================\n")


if __name__ == "__main__":
    train_model()
