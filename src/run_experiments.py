# ===================================================
# run_experiments.py
# ===================================================
# Runs the full Direction A/B reverse-validation + full-period hindsight
# check for a single ticker. Lives in src/ so it can be imported by both
# main_analysis.py and any visual/chart script that needs fresh results.

from src.backtest import run_backtest, run_grid_search, display_results
from src.data import get_price_data


def run_all_experiments(ticker, window_pairs):
    print(f"\n{'='*60}")
    print(f"RUNNING EXPERIMENTS FOR: {ticker}")
    print(f"{'='*60}")

    df_30yr = get_price_data(ticker, start="1996-01-01")

    split_date = "2011-01-01"
    first_half = df_30yr[df_30yr.index < split_date]
    second_half = df_30yr[df_30yr.index >= split_date]

    print(f"First Half:  {first_half.index.min().date()} to {first_half.index.max().date()} ({len(first_half)} days)")
    print(f"Second Half: {second_half.index.min().date()} to {second_half.index.max().date()} ({len(second_half)} days)")

    # --- Direction A ---
    results_a = run_grid_search(first_half, window_pairs)
    display_results(results_a, f"[{ticker}] Direction A Training (1996-2011)")

    best_a = results_a.iloc[0]
    best_short_a, best_long_a = int(best_a["Short_Window"]), int(best_a["Long_Window"])
    train_excess_a = best_a["Excess_Return"]

    (test_market_a, test_strategy_a, test_market_sharpe_a, test_strategy_sharpe_a,
     test_market_dd_a, test_strategy_dd_a) = run_backtest(
        second_half, short_window=best_short_a, long_window=best_long_a
    )
    test_excess_a = test_strategy_a - test_market_a

    print(f"\n--- [{ticker}] Direction A Out-of-Sample Test: SMA({best_short_a}, {best_long_a}) on 2011-2026 ---")
    print(f"Buy & Hold Return:       {test_market_a:.2%}")
    print(f"Strategy Return:         {test_strategy_a:.2%}")
    print(f"Excess Return:           {test_excess_a:.2%}")
    print(f"Buy & Hold Sharpe:       {test_market_sharpe_a:.2f}")
    print(f"Strategy Sharpe:         {test_strategy_sharpe_a:.2f}")
    print(f"Buy & Hold Max Drawdown: {test_market_dd_a:.2%}")
    print(f"Strategy Max Drawdown:   {test_strategy_dd_a:.2%}")

    # --- Direction B ---
    results_b = run_grid_search(second_half, window_pairs)
    display_results(results_b, f"[{ticker}] Direction B Training (2011-2026)")

    best_b = results_b.iloc[0]
    best_short_b, best_long_b = int(best_b["Short_Window"]), int(best_b["Long_Window"])
    train_excess_b = best_b["Excess_Return"]

    (test_market_b, test_strategy_b, test_market_sharpe_b, test_strategy_sharpe_b,
     test_market_dd_b, test_strategy_dd_b) = run_backtest(
        first_half, short_window=best_short_b, long_window=best_long_b
    )
    test_excess_b = test_strategy_b - test_market_b

    print(f"\n--- [{ticker}] Direction B Out-of-Sample Test: SMA({best_short_b}, {best_long_b}) on 1996-2011 ---")
    print(f"Buy & Hold Return:       {test_market_b:.2%}")
    print(f"Strategy Return:         {test_strategy_b:.2%}")
    print(f"Excess Return:           {test_excess_b:.2%}")
    print(f"Buy & Hold Sharpe:       {test_market_sharpe_b:.2f}")
    print(f"Strategy Sharpe:         {test_strategy_sharpe_b:.2f}")
    print(f"Buy & Hold Max Drawdown: {test_market_dd_b:.2%}")
    print(f"Strategy Max Drawdown:   {test_strategy_dd_b:.2%}")

    # --- Hindsight check ---
    results_full = run_grid_search(df_30yr, window_pairs)
    display_results(results_full, f"[{ticker}] Hindsight Check: All Windows Across Full 30 Years")

    return {
        "ticker": ticker,
        "results_a": results_a,
        "results_b": results_b,
        "results_full": results_full,
        "best_short_a": best_short_a, "best_long_a": best_long_a,
        "train_excess_a": train_excess_a, "test_excess_a": test_excess_a,
        "best_short_b": best_short_b, "best_long_b": best_long_b,
        "train_excess_b": train_excess_b, "test_excess_b": test_excess_b,
    }