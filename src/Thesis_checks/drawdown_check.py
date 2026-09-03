# ===================================================
# drawdown_check.py
# ===================================================
# Thesis Check 3: does SMA crossover consistently reduce Max Drawdown vs
# buy-and-hold across all tickers, and does that protection weaken for
# long windows of 150+ days?

import pandas as pd


def check_drawdown_protection(all_results):
    drawdown_rows = []

    for ticker, result in all_results.items():
        full = result["results_full"]

        pairs_protected = (full["Strategy_max_dd"] > full["Market_max_dd"]).sum()
        total_pairs = len(full)
        pct_protected = pairs_protected / total_pairs

        short_long_window = full[full["Long_Window"] < 150]
        long_long_window = full[full["Long_Window"] >= 150]

        avg_dd_below_150 = short_long_window["Strategy_max_dd"].mean()
        avg_dd_at_or_above_150 = long_long_window["Strategy_max_dd"].mean()
        market_dd = full["Market_max_dd"].iloc[0]

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

    return drawdown_df