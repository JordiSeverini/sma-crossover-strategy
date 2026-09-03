# ===================================================
# instability_check.py
# ===================================================
# Thesis Check 2: does the "best" window pair shift meaningfully
# depending on which period was used for training, across all tickers?

import pandas as pd


def check_parameter_instability(all_results):
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

    return instability_df