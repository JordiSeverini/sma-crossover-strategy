# ===================================================
# main_analysis.py
# ===================================================
# Runs the actual SMA crossover experiments, using the reusable functions
# imported from src/backtest.py and src/data.py rather than redefining
# any logic here.

import sys
import os

# main_analysis.py lives in analysis/, but backtest.py and data.py live in
# src/ (a sibling folder) -- Python won't look there by default, so this
# adds the project's root folder to Python's import search path, letting
# "from src.backtest import ..." find them.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.backtest import run_backtest, run_grid_search, display_results
from src.data import get_price_data

Ticker = "AAPL"


# ===================================================
# DOWNLOAD DATA #
# ===================================================
# 30 years of history -- every experiment below slices whatever period
# it needs out of this one DataFrame instead of re-downloading.
df_30yr = get_price_data(Ticker, start="1996-01-01")


# ===================================================
# WINDOW COMBINATIONS TO TEST #
# ===================================================
# Sweep ranges to naturally include well-known pairs
# (5,20), (9,21), (10,20), (12,26), (50,200)
short_windows = [5, 9, 10, 12, 15, 20, 25, 30]
long_windows = [20, 21, 26, 50, 100, 150, 200]

window_pairs = []
for short_w in short_windows:
    for long_w in long_windows:
        if short_w < long_w:
            window_pairs.append((short_w, long_w))


# =============================================================
# 30-YEAR REVERSE VALIDATION -- two 15-year halves, tested both directions
# =============================================================
split_date = "2011-01-01"

first_half = df_30yr[df_30yr.index < split_date]
second_half = df_30yr[df_30yr.index >= split_date]

print(f"First Half:  {first_half.index.min().date()} to {first_half.index.max().date()} ({len(first_half)} days)")
print(f"Second Half: {second_half.index.min().date()} to {second_half.index.max().date()} ({len(second_half)} days)")


# --- Direction A: train on first half, test on second half ---
results_a = run_grid_search(first_half, window_pairs)
display_results(results_a, "Direction A Training (1996-2011)")

best_a = results_a.iloc[0]
best_short_a, best_long_a = int(best_a["Short_Window"]), int(best_a["Long_Window"])

test_market_a, test_strategy_a, test_market_sharpe_a, test_strategy_sharpe_a,  test_market_dd_a, test_strategy_dd_a = run_backtest(second_half, short_window=best_short_a, long_window=best_long_a)

print(f"\n--- Direction A Out-of-Sample Test: SMA({best_short_a}, {best_long_a}) on 2011-2026 ---")
print(f"Buy & Hold Return:  {test_market_a:.2%}")
print(f"Strategy Return:    {test_strategy_a:.2%}")
print(f"Excess Return:      {(test_strategy_a - test_market_a):.2%}")
print(f"Buy & Hold Sharpe:  {test_market_sharpe_a:.2f}")
print(f"Strategy Sharpe:    {test_strategy_sharpe_a:.2f}")
print(f"Buy & Hold Max Drawdown:{test_market_dd_a:.2%}")
print(f"Strategy Max Drawdown : {test_strategy_dd_a:.2%}")


# --- Direction B: train on second half, test on first half ---
results_b = run_grid_search(second_half, window_pairs)
display_results(results_b, "Direction B Training (2011-2026)")

best_b = results_b.iloc[0]
best_short_b, best_long_b = int(best_b["Short_Window"]), int(best_b["Long_Window"])

test_market_b, test_strategy_b, test_market_sharpe_b, test_strategy_sharpe_b, test_market_dd_b, test_strategy_dd_b = run_backtest(first_half, short_window=best_short_b, long_window=best_long_b)

print(f"\n--- Direction B Out-of-Sample Test: SMA({best_short_b}, {best_long_b}) on 1996-2011 ---")
print(f"Buy & Hold Return:  {test_market_b:.2%}")
print(f"Strategy Return:    {test_strategy_b:.2%}")
print(f"Excess Return:      {(test_strategy_b - test_market_b):.2%}")
print(f"Buy & Hold Sharpe:  {test_market_sharpe_b:.2f}")
print(f"Strategy Sharpe:    {test_strategy_sharpe_b:.2f}")
print(f"Buy & Hold Max Drawdown:{test_market_dd_b:.2%}")
print(f"Strategy Max Drawdown : {test_strategy_dd_b:.2%}")


# =============================================================
# DIAGNOSTIC: does ANY window pair beat buy-and-hold across the ENTIRE
# 30-year period, even with the benefit of hindsight?
# =============================================================
# NOTE: this is NOT a valid trading strategy -- it uses hindsight, since you
# could never have picked a window in 1996 based on data through 2026. It only
# answers a narrower question: does the best-case ceiling for this strategy
# family clear buy-and-hold at all over the full 30 years, or does NOTHING
# beat it even in hindsight?
results_full_period = run_grid_search(df_30yr, window_pairs)
display_results(results_full_period, "Hindsight Check: All Windows Across Full 30 Years (1996-2026)")