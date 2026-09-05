# ===================================================
# main_analysis.py
# ===================================================
# Runs the actual SMA crossover experiments, using the reusable functions
# imported from src/backtest.py and src/data.py rather than redefining
# any logic here.

import sys
import os
import pandas as pd
import pickle 

# main_analysis.py lives in analysis/, but backtest.py and data.py live in
# src/ (a sibling folder) -- Python won't look there by default, so this
# adds the project's root folder to Python's import search path, letting
# "from src.backtest import ..." find them.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.run_experiments import run_all_experiments
from src.backtest import run_backtest, run_grid_search, display_results
from src.data import get_price_data
from src.Thesis_checks.overfitting_check import check_overfitting
from src.Thesis_checks.instability_check import check_parameter_instability
from src.Thesis_checks.drawdown_check import check_drawdown_protection


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

# ===================================================
# RUN FOR ALL TICKERS #
# ===================================================
tickers = ["AAPL", "SPY", "DIS", "KO"]

all_results = {}
for ticker in tickers:
    all_results[ticker] = run_all_experiments(ticker, window_pairs)

# Save all_results so chart scripts can load it instantly, without
# re-running the full four-ticker experiment suite every time
os.makedirs("outputs", exist_ok=True)
with open("outputs/all_results.pkl", "wb") as f:
    pickle.dump(all_results, f)
print("\nSaved all_results to outputs/all_results.pkl")

# ===================================================
# SUMMARY ACROSS ALL TICKERS #
# ===================================================
# Takes the Best perfomring windows from each ticker over the 30 year Hindsight window
# Breaks the information down for comparison across tickers

summary_rows = []

for ticker, result in all_results.items():
    best_full = result["results_full"].iloc[0]  # top row = best Excess_Return, full 30-year hindsight

    summary_rows.append({
        "Ticker": ticker,
        "Best_Short": int(best_full["Short_Window"]),
        "Best_Long": int(best_full["Long_Window"]),
        "Buy_Hold_Return": best_full["Buy_Hold_Return"],
        "Strategy_Return": best_full["Strategy_Return"],
        "Excess_Return": best_full["Excess_Return"],
        "Buy_&_Hold_Sharpe": best_full["Buy_&_Hold_Sharpe"],
        "Strategy_Sharpe": best_full["Strategy_Sharpe"],
        "Market_max_dd": best_full["Market_max_dd"],
        "Strategy_max_dd": best_full["Strategy_max_dd"]
    })

summary_df = pd.DataFrame(summary_rows)

print(f"\n{'='*60}")
print("SUMMARY: BEST HINDSIGHT WINDOW PAIR PER TICKER")
print(f"{'='*60}")
display_results(summary_df, "Cross-Ticker Summary")

# =================================================
# Thesis Checks
# ================================================
overfitting_df = check_overfitting(all_results)
instability_df = check_parameter_instability(all_results)
drawdown_df = check_drawdown_protection(all_results)