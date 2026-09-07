# ===================================================
# drawdown_chart.py
# ===================================================
# Max Drawdown vs Long_Window, one subplot per ticker, with buy-and-hold's
# drawdown as a reference line -- visualizes Thesis Check 3, including
# whether the ~150-day threshold effect holds per ticker.

import sys
import os
import pickle
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

with open(os.path.join(os.path.dirname(__file__), "..", "outputs", "all_results.pkl"), "rb") as f:
    all_results = pickle.load(f)

tickers = list(all_results.keys())

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
axes = axes.flatten()  # turn the 2x2 grid into a flat list of 4, easier to loop over

for i, ticker in enumerate(tickers):
    ax = axes[i]
    full = all_results[ticker]["results_full"]

    # Sort by Long_Window so the line reads left-to-right in increasing order
    full_sorted = full.sort_values("Long_Window")

    ax.scatter(full_sorted["Long_Window"], full_sorted["Strategy_max_dd"],
               color="steelblue", alpha=0.6, s=40, label="Strategy (each window pair)")

    market_dd = full["Market_max_dd"].iloc[0]
    ax.axhline(market_dd, color="black", linestyle="--", linewidth=1.2, label=f"Buy & Hold ({market_dd:.1%})")

    # Mark the 150-day threshold with a vertical line for reference
    ax.axvline(150, color="gray", linestyle=":", linewidth=1, alpha=0.7)

    ax.set_title(ticker)
    ax.set_xlabel("Long Window")
    ax.set_ylabel("Max Drawdown")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

fig.suptitle("Max Drawdown vs Long Window, by Ticker (dashed line = Buy & Hold, dotted = 150-day mark)", fontsize=13)
plt.tight_layout()
os.makedirs("outputs/figures", exist_ok=True)
plt.savefig("outputs/figures/drawdown_by_window.png", dpi=150)
print("Saved to outputs/figures/drawdown_by_window.png")
plt.show()