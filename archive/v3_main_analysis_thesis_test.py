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

# ===================================================
# THESIS CHECK 1: OVERFITTING PATTERN #
# ===================================================
# Verifies: does the window pair that wins during training consistently
# fail once tested on unseen data, across ALL four tickers?
overfitting_rows = []

for ticker, result in all_results.items():
    overfitting_rows.append({
        "Ticker": ticker,
        "DirA_Train_Excess": result["train_excess_a"],
        "DirA_Test_Excess": result["test_excess_a"],
        "DirA_Overfit_Confirmed": result["train_excess_a"] > 0 and result["test_excess_a"] < 0,
        "DirB_Train_Excess": result["train_excess_b"],
        "DirB_Test_Excess": result["test_excess_b"],
        "DirB_Overfit_Confirmed": result["train_excess_b"] > 0 and result["test_excess_b"] < 0,
    })

overfitting_df = pd.DataFrame(overfitting_rows)

print(f"\n{'='*60}")
print("THESIS CHECK 1: OVERFITTING PATTERN")
print(f"{'='*60}")

display_overfit = overfitting_df.copy()
for col in ["DirA_Train_Excess", "DirA_Test_Excess", "DirB_Train_Excess", "DirB_Test_Excess"]:
    display_overfit[col] = display_overfit[col].apply(lambda x: f"{x:.2%}")
print(display_overfit.to_string(index=False))

# ===================================================
# THESIS CHECK 2: PARAMETER INSTABILITY #
# ===================================================
# Verifies: does the "best" window pair shift meaningfully depending on
# which period was used for training, across ALL four tickers?
instability_rows = []

for ticker, result in all_results.items():
    short_a, long_a = result["best_short_a"], result["best_long_a"]
    short_b, long_b = result["best_short_b"], result["best_long_b"]

    instability_rows.append({
        "Ticker": ticker,
        "DirA_Best_Window": f"({short_a},{long_a})",
        "DirB_Best_Window": f"({short_b},{long_b})",
        "Short_Diff": abs(short_a - short_b),
        "Long_Diff": abs(long_a - long_b),
        "Same_Window": (short_a == short_b) and (long_a == long_b),
    })

instability_df = pd.DataFrame(instability_rows)

print(f"\n{'='*60}")
print("THESIS CHECK 2: PARAMETER INSTABILITY")
print(f"{'='*60}")
print(instability_df.to_string(index=False))

# ===================================================
# THESIS CHECK 3: DRAWDOWN PROTECTION #
# ===================================================
# Verifies: does SMA crossover consistently reduce Max Drawdown vs
# buy-and-hold, across ALL four tickers -- and does that protection
# weaken for long windows of 150+ days, as seen with AAPL?
drawdown_rows = []

for ticker, result in all_results.items():
    full = result["results_full"]

    # % of all window pairs where the strategy's drawdown was smaller
    # (less negative / better) than buy-and-hold's
    pairs_protected = (full["Strategy_max_dd"] > full["Market_max_dd"]).sum()
    total_pairs = len(full)
    pct_protected = pairs_protected / total_pairs

    # Split into "short/medium" long-windows (<150) vs "long" (>=150)
    # to check whether protection weakens past the threshold
    short_long_window = full[full["Long_Window"] < 150]
    long_long_window = full[full["Long_Window"] >= 150]

    avg_dd_below_150 = short_long_window["Strategy_max_dd"].mean()
    avg_dd_at_or_above_150 = long_long_window["Strategy_max_dd"].mean()
    market_dd = full["Market_max_dd"].iloc[0]  # same for every row within a ticker

    drawdown_rows.append({
        "Ticker": ticker,
        "Market_MaxDD": market_dd,
        "Pct_Pairs_Protected": pct_protected,
        "Avg_Strategy_DD_(LongWin<150)": avg_dd_below_150,
        "Avg_Strategy_DD_(LongWin>=150)": avg_dd_at_or_above_150,
    })

drawdown_df = pd.DataFrame(drawdown_rows)

print(f"\n{'='*60}")
print("THESIS CHECK 3: DRAWDOWN PROTECTION")
print(f"{'='*60}")

display_dd = drawdown_df.copy()
for col in ["Market_MaxDD", "Pct_Pairs_Protected", "Avg_Strategy_DD_(LongWin<150)", "Avg_Strategy_DD_(LongWin>=150)"]:
    display_dd[col] = display_dd[col].apply(lambda x: f"{x:.2%}")
print(display_dd.to_string(index=False))