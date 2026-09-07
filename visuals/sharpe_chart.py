# ===================================================
# sharpe_chart.py
# ===================================================
# Bar chart: Buy & Hold Sharpe vs Strategy Sharpe, one pair per ticker
# (using each ticker's best hindsight window pair).

import sys
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

with open(os.path.join(os.path.dirname(__file__), "..", "outputs", "all_results.pkl"), "rb") as f:
    all_results = pickle.load(f)

tickers = []
market_sharpes = []
strategy_sharpes = []

for ticker, result in all_results.items():
    best_full = result["results_full"].iloc[0]  # top row = best Excess_Return, full 30-year hindsight
    tickers.append(ticker)
    market_sharpes.append(best_full["Buy_&_Hold_Sharpe"])
    strategy_sharpes.append(best_full["Strategy_Sharpe"])

x = np.arange(len(tickers))
bar_width = 0.35

fig, ax = plt.subplots(figsize=(9, 6))

ax.bar(x - bar_width/2, market_sharpes, bar_width, label="Buy & Hold", color="black")
ax.bar(x + bar_width/2, strategy_sharpes, bar_width, label="Strategy (Best Window)", color="steelblue")

ax.set_xticks(x)
ax.set_xticklabels(tickers)
ax.set_ylabel("Sharpe Ratio")
ax.set_title("Sharpe Ratio: Buy & Hold vs. Best-Performing Strategy, by Ticker")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
os.makedirs("outputs/figures", exist_ok=True)
plt.savefig("outputs/figures/sharpe_comparison.png", dpi=150)
print("Saved to outputs/figures/sharpe_comparison.png")
plt.show()