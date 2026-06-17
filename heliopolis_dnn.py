import os
import sys
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

    def forward(self, x: torch.Tensor) -> torch. torch.Tensor:
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

def generate_synthetic_malaysian_solar_data(num_samples: int = 500) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generates realistic, synthetic site-due-diligence data for 500 prospects across Malaysia.
    Input Features (6):
      1. Land Area (sqm) [ranging from 10k to 200k]
      2. Mean Slope (degrees) [0 to 45 deg]
      3. Max Slope (degrees) [0 to 75 deg]
      4. Substation Grid Proximity (km) [0.5 to 15.0 km]
      5. Co-owners count [1 to 15 owners]
      6. GHI solar irradiance (kWh/m2/year) [1400 to 1700]
    """
    np.random.seed(42) # Set seed for 100% deterministic reproducibility
    
    # Feature inputs
    area = np.random.uniform(10000, 200000, (num_samples, 1))
    mean_slope = np.random.uniform(0, 45, (num_samples, 1))
    max_slope = mean_slope + np.random.uniform(0, 30, (num_samples, 1))
    grid_dist = np.random.uniform(0.5, 15.0, (num_samples, 1))
    owners_count = np.random.randint(1, 15, (num_samples, 1)).astype(np.float32)
    ghi = np.random.uniform(1400, 1700, (num_samples, 1))
    
    X = np.hstack([area, mean_slope, max_slope, grid_dist, owners_count, ghi])
    
    # Ground-truth Label 1: Feasibility Success (True if slope < 15, grid_dist < 5, and owners < 5)
    feasibility = []
    for i in range(num_samples):
        is_feasible = 1.0 if (X[i, 1] < 15.0 and X[i, 3] < 6.0 and X[i, 4] < 5.0) else 0.0
        feasibility.append(is_feasible)
    y_class = np.array(feasibility, dtype=np.float32).reshape(-1, 1)
    
    # Ground-truth Label 2: Optimized LCOE
    # Base LCOE RM 0.20, increases with higher slope (civil grading), greater grid distance, and smaller area
    y_reg = 0.20 + (X[:, 1:2] * 0.005) + (X[:, 3:4] * 0.015) - (X[:, 0:1] * 0.0000002) + (X[:, 4:5] * 0.002)
    y_reg = np.clip(y_reg, 0.18, 0.65).astype(np.float32)
    
    # Normalize features to mean=0, std=1 for training stability (z-score)
    X_mean = np.mean(X, axis=0)
    X_std = np.std(X, axis=0) + 1e-12 # Protect against division by zero
    X_normalized = (X - X_mean) / X_std
    
    # Save normalization constants
    norm_constants = {"mean": X_mean.tolist(), "std": X_std.tolist()}
    with open(r"C:\Users\lewka\deep_learning\MAIC Nexus Challenge\normalization_constants.json", "w") as f:
        json.dump(norm_constants, f, indent=4)
        
    return X_normalized, y_class, y_reg


def train_model():
    print("=== HELIOPOLIS-AI DEEP LEARNING TRAINING PIPELINE ===\n")
    models_dir = r"C:\Users\lewka\deep_learning\MAIC Nexus Challenge\models"
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Generate and prepare training data
    X, y_class, y_reg = generate_synthetic_malaysian_solar_data(num_samples=500)
    
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
