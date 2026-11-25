"""
Hybrid Machine Learning Coupling Example for SU2
-------------------------------------------------------------------------
This script demonstrates how to couple the SU2 CFD solver with a 
PyTorch training loop in real-time using the Python Wrapper (pysu2).

Usage:
    python3 train_online.py
"""

# Standard Library Imports
import sys

# Hard Dependency: SU2 Wrapper & MPI
# (These must exist for the tutorial to run at all)
import pysu2
from mpi4py import MPI

# Optional Dependency: PyTorch
# (We handle the case where the user/server doesn't have ML libraries)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    print("\n[WARNING] PyTorch not found. ML features will be disabled.\n")

# --- 1. Define Surrogate Model (Conditional) ---
if HAS_TORCH:
    class SurrogateModel(nn.Module):
        def __init__(self):
            super(SurrogateModel, self).__init__()
            self.fc = nn.Linear(1, 1) 
        
        def forward(self, x):
            return self.fc(x)
else:
    # Define as None so the name exists in the namespace
    SurrogateModel = None

def main():
    # Initialize MPI Communicator
    comm = MPI.COMM_WORLD
    
    # Configuration
    config_file = "inv_NACA0012.cfg"
    
    # Initialize Driver
    try:
        driver = pysu2.CSinglezoneDriver(config_file, 1, comm)
    except TypeError:
        print("[Error] Failed to initialize driver. Ensure SU2 is compiled with MPI support.")
        sys.exit(1)

    driver.Preprocess(0)

    # Initialize ML Model (Only if Torch is available)
    if HAS_TORCH:
        model = SurrogateModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        print("\n[Hybrid-ML] Models initialized. Starting coupled loop...\n")
    else:
        model = None
        optimizer = None
        print("\n[Hybrid-ML] Running in PHYSICS-ONLY mode (No ML).\n")

    # --- Hybrid Simulation Loop ---
    n_iterations = 10
    
    for i in range(n_iterations):
        # A. Run Physics Step (Always runs)
        driver.Run()
        
        # B. Extract Physics Data (The Bridge)
        try:
            physics_state = driver.GetOutputValue("RMS_DENSITY")
        except Exception:
            # Fallback for testing/dummy runs
            physics_state = 0.0
            
        print(f"  Iter {i}: Physics State (Log Rho) = {physics_state:.6f}")
        
        # C. Online Training Step (Conditional)
        if HAS_TORCH:
            # Train the model to predict the current physics state
            input_tensor = torch.tensor([[float(i)]])
            target_tensor = torch.tensor([[physics_state]])
            
            optimizer.zero_grad()
            prediction = model(input_tensor)
            loss = (prediction - target_tensor) ** 2
            loss.backward()
            optimizer.step()
            
            print(f"  Iter {i}: ML State (MSE Loss)     = {loss.item():.6f}")
        else:
            # If no Torch, we just skip the ML update
            pass

    # Finalize
    driver.Postprocess()
    print("\n[Hybrid-ML] Simulation Complete.")

if __name__ == "__main__":
    main()