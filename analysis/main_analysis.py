# ===================================================
# main_analysis.py
# ===================================================
# Runs the actual SMA crossover experiments, using the reusable functions
# imported from src/backtest.py and src/data.py rather than redefining
# any logic here.

import sys
import os
import pandas as pd


# main_analysis.py lives in analysis/, but backtest.py and data.py live in
# src/ (a sibling folder) -- Python won't look there by default, so this
# adds the project's root folder to Python's import search path, letting
# "from src.backtest import ..." find them.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

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
# ALL-EXPERIMENTS FUNCTION #
# ===================================================
def run_all_experiments(ticker, window_pairs):
    print(f"\n{'='*60}")
    print(f"RUNNING EXPERIMENTS FOR: {ticker}")
    print(f"{'='*60}")

    # DOWNLOAD DATA #
    df_30yr = get_price_data(ticker, start="1996-01-01")

    # SPLIT INTO TWO 15-YEAR HALVES #
    split_date = "2011-01-01"
    first_half = df_30yr[df_30yr.index < split_date]
    second_half = df_30yr[df_30yr.index >= split_date]

    print(f"First Half:  {first_half.index.min().date()} to {first_half.index.max().date()} ({len(first_half)} days)")
    print(f"Second Half: {second_half.index.min().date()} to {second_half.index.max().date()} ({len(second_half)} days)")

    # --- Direction A: train on first half, test on second half ---
    results_a = run_grid_search(first_half, window_pairs)
    display_results(results_a, f"[{ticker}] Direction A Training (1996-2011)")

    # best_a isolates and stores the first dict row of the resuts_a
    best_a = results_a.iloc[0]
    # Stores the best_short_a and best_long _a by accessing the short_window and long_window coumns
    best_short_a, best_long_a = int(best_a["Short_Window"]), int(best_a["Long_Window"])
    # The excess return of whichever window pair scored best during Training
    train_excess_a = best_a["Excess_Return"]

    (test_market_a, test_strategy_a,test_market_sharpe_a, test_strategy_sharpe_a,test_market_dd_a, test_strategy_dd_a) = run_backtest(second_half, short_window=best_short_a, long_window=best_long_a)
    # the excess return of that same specific window pair when it's re-run on Direction A's test data
    test_excess_a = test_strategy_a - test_market_a

    print(f"\n--- [{ticker}] Direction A Out-of-Sample Test: SMA({best_short_a}, {best_long_a}) on 2011-2026 ---")
    print(f"Buy & Hold Return:       {test_market_a:.2%}")
    print(f"Strategy Return:         {test_strategy_a:.2%}")
    print(f"Excess Return:           {test_excess_a:.2%}")
    print(f"Buy & Hold Sharpe:       {test_market_sharpe_a:.2f}")
    print(f"Strategy Sharpe:         {test_strategy_sharpe_a:.2f}")
    print(f"Buy & Hold Max Drawdown: {test_market_dd_a:.2%}")
    print(f"Strategy Max Drawdown:   {test_strategy_dd_a:.2%}")

    # --- Direction B: train on second half, test on first half ---
    results_b = run_grid_search(second_half, window_pairs)
    display_results(results_b, f"[{ticker}] Direction B Training (2011-2026)")

    # best_a isolates and stores the first dict row of the resuts_b
    best_b = results_b.iloc[0]
    # Stores the best_short_b and best_long _b by accessing the short_window and long_window coumns
    best_short_b, best_long_b = int(best_b["Short_Window"]), int(best_b["Long_Window"])
    # The excess return of whichever window pair scored best during Training
    train_excess_b = best_b["Excess_Return"]

    (test_market_b, test_strategy_b,test_market_sharpe_b, test_strategy_sharpe_b,test_market_dd_b, test_strategy_dd_b) = run_backtest(first_half, short_window=best_short_b, long_window=best_long_b)
    # The excess return of that same specific window pair when it's re-run on Direction B's test data
    test_excess_b = test_strategy_b - test_market_b

    print(f"\n--- [{ticker}] Direction B Out-of-Sample Test: SMA({best_short_b}, {best_long_b}) on 1996-2011 ---")
    print(f"Buy & Hold Return:       {test_market_b:.2%}")
    print(f"Strategy Return:         {test_strategy_b:.2%}")
    print(f"Excess Return:           {test_excess_b:.2%}")
    print(f"Buy & Hold Sharpe:       {test_market_sharpe_b:.2f}")
    print(f"Strategy Sharpe:         {test_strategy_sharpe_b:.2f}")
    print(f"Buy & Hold Max Drawdown: {test_market_dd_b:.2%}")
    print(f"Strategy Max Drawdown:   {test_strategy_dd_b:.2%}")

    # --- Hindsight check across full 30 years ---
    results_full = run_grid_search(df_30yr, window_pairs)
    display_results(results_full, f"[{ticker}] Hindsight Check: All Windows Across Full 30 Years")

    # Return a summary to compare tickers side by side later
    return {
        "ticker": ticker,
        "results_a": results_a,
        "results_b": results_b,
        "results_full": results_full,
        "best_short_a": best_short_a, 
        "best_long_a": best_long_a,
        "train_excess_a": train_excess_a, 
        "test_excess_a": test_excess_a,
        "best_short_b": best_short_b, 
        "best_long_b": best_long_b,
        "train_excess_b": train_excess_b, 
        "test_excess_b": test_excess_b,
    }

# ===================================================
# RUN FOR ALL TICKERS #
# ===================================================
tickers = ["AAPL", "SPY", "DIS", "KO"]

all_results = {}
for ticker in tickers:
    all_results[ticker] = run_all_experiments(ticker, window_pairs)


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