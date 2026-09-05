# ===================================================
# overfitting_chart.py
# ===================================================
# Grouped bar chart: training excess return vs test excess return,
# for all 4 tickers, both directions -- visualizes Thesis Check 1.

import sys
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.Thesis_checks.overfitting_check import check_overfitting

# Load already-computed results instead of re-running the four-ticker suite
with open(os.path.join(os.path.dirname(__file__), "..", "outputs", "all_results.pkl"), "rb") as f:
    all_results = pickle.load(f)

overfitting_df = check_overfitting(all_results)

# --- Plotting code ---
tickers = overfitting_df["Ticker"].tolist()
x = np.arange(len(tickers))
bar_width = 0.2

fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(x - 1.5*bar_width, overfitting_df["DirA_Train_Excess"], bar_width, label="Dir A Train", color="steelblue")
ax.bar(x - 0.5*bar_width, overfitting_df["DirA_Test_Excess"], bar_width, label="Dir A Test", color="lightblue")
ax.bar(x + 0.5*bar_width, overfitting_df["DirB_Train_Excess"], bar_width, label="Dir B Train", color="darkorange")
ax.bar(x + 1.5*bar_width, overfitting_df["DirB_Test_Excess"], bar_width, label="Dir B Test", color="moccasin")

ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(tickers)
ax.set_ylabel("Excess Return (%)")
ax.set_title("Overfitting Pattern: Training vs Test Excess Return, by Ticker")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
os.makedirs("outputs/figures", exist_ok=True)
plt.savefig("outputs/figures/overfitting_pattern.png", dpi=150)
print("Saved to outputs/figures/overfitting_pattern.png")
plt.show()