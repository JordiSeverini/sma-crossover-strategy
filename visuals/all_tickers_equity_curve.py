# ===================================================
# all_tickers_equity_curve.py
# ===================================================
# 2x2 grid: each ticker's buy-and-hold vs. its best-performing (hindsight)
# window pair, cumulative growth of $1, over the full 30 years. Each
# subplot's y-axis scale (log vs linear) is chosen based on that ticker's
# own growth magnitude

import sys
import os
import pickle
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.backtest import build_backtest_dataframe
from src.data import get_price_data

with open(os.path.join(os.path.dirname(__file__), "..", "outputs", "all_results.pkl"), "rb") as f:
    all_results = pickle.load(f)

tickers = list(all_results.keys())

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
axes = axes.flatten()

# Threshold: if the buy-and-hold line grew by more than this multiple,
# a linear scale would flatten the strategy line, so use log instead.
LOG_SCALE_THRESHOLD = 50

for i, ticker in enumerate(tickers):
    ax = axes[i]
    result = all_results[ticker]

    best_full = result["results_full"].iloc[0]
    best_short = int(best_full["Short_Window"])
    best_long = int(best_full["Long_Window"])

    df_full = get_price_data(ticker, start="1996-01-01")
    df = build_backtest_dataframe(df_full, best_short, best_long)

    ax.plot(df.index, df["Cumulative_Market"], label="Buy & Hold", color="black", linewidth=1.3)
    ax.plot(df.index, df["Cumulative_Strategy"], label=f"SMA({best_short},{best_long})", color="steelblue", linewidth=1.3)

    # Decide scale based on this ticker's own final buy-and-hold growth multiple
    final_market_growth = df["Cumulative_Market"].iloc[-1]
    if final_market_growth > LOG_SCALE_THRESHOLD:
        ax.set_yscale("log")
        scale_label = "log"
    else:
        scale_label = "linear"

    ax.set_title(ticker)
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Growth of $1 ({scale_label})")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

fig.suptitle("Buy & Hold vs. Best-Performing Strategy (Full-Period Hindsight), by Ticker, 1996-2026", fontsize=13)
plt.tight_layout()
os.makedirs("outputs/figures", exist_ok=True)
plt.savefig("outputs/figures/all_tickers_equity_curves.png", dpi=150)
print("Saved to outputs/figures/all_tickers_equity_curves.png")
plt.show()