# ===================================================
# overfitting_check.py
# ===================================================
# Thesis Check 1: does the window pair that wins during training
# consistently fail once tested on unseen data, across all tickers?

import pandas as pd


def check_overfitting(all_results):
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

    return overfitting_df