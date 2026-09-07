# ===================================================
# instability_chart.py
# ===================================================
# Scatter plot connecting each ticker's Direction A winning window pair
# to its Direction B winning pair. If the strategy had a genuine, stable
# "best fit" window, both points would overlap. Instead, they consistently
# land apart -- demonstrating no stable optimum exists.

import sys
import os
import pickle
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

with open(os.path.join(os.path.dirname(__file__), "..", "outputs", "all_results.pkl"), "rb") as f:
    all_results = pickle.load(f)

fig, ax = plt.subplots(figsize=(9, 7))

colors = {"AAPL": "steelblue", "SPY": "darkorange", "DIS": "seagreen", "KO": "firebrick"}

for ticker, result in all_results.items():
    short_a, long_a = result["best_short_a"], result["best_long_a"]
    short_b, long_b = result["best_short_b"], result["best_long_b"]
    color = colors.get(ticker, "gray")

    # The line itself IS the evidence -- its length shows how far apart
    # the two "optimal" answers landed, depending purely on which period
    # was used to search for them
    ax.plot([short_a, short_b], [long_a, long_b], color=color, linestyle="--", alpha=0.6, linewidth=1.5)

    ax.scatter(short_a, long_a, color=color, marker="o", s=140, zorder=3)
    ax.scatter(short_b, long_b, color=color, marker="s", s=140, zorder=3)

    # Label each point with its actual window pair and ticker name
    ax.annotate(f"{ticker}\nDir A: ({short_a},{long_a})", (short_a, long_a),
                textcoords="offset points", xytext=(8, 8), fontsize=8, color=color)
    ax.annotate(f"{ticker}\nDir B: ({short_b},{long_b})", (short_b, long_b),
                textcoords="offset points", xytext=(8, -14), fontsize=8, color=color)

ax.set_xlabel("Short Window")
ax.set_ylabel("Long Window")
ax.set_title("No Stable 'Best Fit': Direction A vs Direction B Winning Windows Never Match")
ax.grid(True, alpha=0.3)

# Simple legend explaining the two marker shapes (not per-ticker, since
# labels already identify tickers directly on the chart)
ax.scatter([], [], color="gray", marker="o", s=100, label="Direction A winner")
ax.scatter([], [], color="gray", marker="s", s=100, label="Direction B winner")
ax.legend(loc="lower left")

plt.tight_layout()
os.makedirs("outputs/figures", exist_ok=True)
plt.savefig("outputs/figures/parameter_instability.png", dpi=150)
print("Saved to outputs/figures/parameter_instability.png")
plt.show()