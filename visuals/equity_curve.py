# ===================================================
# equity_curve.py
# ===================================================
# Plots the strategy's cumulative growth vs buy-and-hold over time,
# for a single ticker and window pair.

import sys
import os
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.backtest import build_backtest_dataframe
from src.data import get_price_data

# Use AAPL's best hindsight pair from your summary table: SMA(5, 150)
ticker = "AAPL"
short_window, long_window = 5, 150

df_full = get_price_data(ticker, start="1996-01-01")
df = build_backtest_dataframe(df_full, short_window, long_window)

plt.figure(figsize=(12, 6))
plt.plot(df.index, df["Cumulative_Market"], label="Buy & Hold", color="black", linewidth=1.5)
plt.plot(df.index, df["Cumulative_Strategy"], label=f"SMA({short_window},{long_window}) Strategy", color="steelblue", linewidth=1.5)

plt.title(f"{ticker}: Strategy vs Buy & Hold, Growth of $1 (1996-2026)")
plt.xlabel("Date")
plt.ylabel("Growth of $1 (log scale)")
plt.yscale("log")  # log scale, since AAPL's growth is so extreme a linear scale would flatten the strategy line
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

os.makedirs("outputs/figures", exist_ok=True)
plt.savefig("outputs/figures/aapl_equity_curve.png", dpi=150)
print("Saved to outputs/figures/aapl_equity_curve.png")
plt.show()


