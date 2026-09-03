# IMPORT LIBRARIES #
#############################################
import yfinance as yf 
import pandas as pd 
import numpy as np 
from datetime import datetime

Ticker = "AAPL"

# DOWNLOAD DATA -- SINGLE SOURCE FOR BOTH EXPERIMENTS #
#############################################
# Downloads enough history to cover both experiments below (2018 onward).
# Each experiment slices whatever period it needs out of this one DataFrame.
df = yf.download(Ticker, start="2018-01-01", end=datetime.now(), multi_level_index=False)


# BACKTEST FUNCTION #
#############################################
def run_backtest(price_df, short_window, long_window):
    df = price_df.copy()

    df["SMA_SHORT"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_LONG"] = df["Close"].rolling(window=long_window).mean()

    df["Signal"] = np.where(df["SMA_SHORT"] > df["SMA_LONG"], 1, 0)
    df.loc[df["SMA_LONG"].isna(), "Signal"] = np.nan

    df["Position"] = df["Signal"].diff().map({1: "BUY", -1: "SELL", 0: "HOLD"})
    df.loc[df["SMA_LONG"].isna(), "Position"] = None

    df["Market_Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Market_Return"] * df["Signal"].shift(1)

    df["Cumulative_Market"] = (1 + df["Market_Return"]).cumprod()
    df["Cumulative_Strategy"] = (1 + df["Strategy_Return"]).cumprod()

    total_market_return = df["Cumulative_Market"].iloc[-1] - 1
    total_strategy_return = df["Cumulative_Strategy"].iloc[-1] - 1

    return total_market_return, total_strategy_return


# WINDOW COMBINATIONS TO TEST #
################################################
short_windows = [5, 10, 15, 20, 25, 30]
long_windows = [50, 100, 150, 200]

window_pairs = []
for short_w in short_windows:
    for long_w in long_windows:
        if short_w < long_w:
            window_pairs.append((short_w, long_w, "Sweep"))

known_pairs = [
    (5, 20, "Known"),
    (10, 20, "Known"),
    (50, 200, "Known"),   # Golden Cross / Death Cross
    (9, 21, "Known"),     # Commonly used in short-term/day-trading SMA crossover
    (12, 26, "Known"),    # MACD-inspired
]

window_pairs.extend(known_pairs)


# =============================================================
# EXPERIMENT 1: BULL MARKET (train 2021-2023, test 2024-2026)
# =============================================================
train_df = df[(df.index >= "2021-01-01") & (df.index < "2024-01-01")]
test_df = df[df.index >= "2024-01-01"]

print(f"[Exp 1] Training Period: {train_df.index.min().date()} to {train_df.index.max().date()} ({len(train_df)} days)")
print(f"[Exp 1] Testing Period:  {test_df.index.min().date()} to {test_df.index.max().date()} ({len(test_df)} days)")

results = []
for short_w, long_w, source in window_pairs:
    market_ret, strategy_ret = run_backtest(train_df, short_window=short_w, long_window=long_w)
    results.append({
        "Short_Window": short_w, "Long_Window": long_w, "Source": source,
        "Buy_Hold_Return": market_ret, "Strategy_Return": strategy_ret,
        "Excess_Return": strategy_ret - market_ret
    })

results_df = pd.DataFrame(results).sort_values("Excess_Return", ascending=False)
display_df = results_df.copy()
for col in ["Buy_Hold_Return", "Strategy_Return", "Excess_Return"]:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")
print(display_df.to_string(index=False))

best_short, best_long = 5, 20
test_market_ret, test_strategy_ret = run_backtest(test_df, short_window=best_short, long_window=best_long)

print(f"\n--- [Exp 1] Out-of-Sample Test: SMA({best_short}, {best_long}) ---")
print(f"Buy & Hold Return (Test Period):  {test_market_ret:.2%}")
print(f"Strategy Return (Test Period):    {test_strategy_ret:.2%}")
print(f"Excess Return (Test Period):      {(test_strategy_ret - test_market_ret):.2%}")


# =============================================================
# EXPERIMENT 2: CRASH PERIOD (train 2018-2019, test 2020 COVID crash)
# =============================================================
train_df_crash = df[(df.index >= "2018-01-01") & (df.index < "2020-01-01")]
test_df_crash = df[(df.index >= "2020-01-01") & (df.index < "2021-01-01")]

print(f"\n[Exp 2] Crash Training Period: {train_df_crash.index.min().date()} to {train_df_crash.index.max().date()} ({len(train_df_crash)} days)")
print(f"[Exp 2] Crash Testing Period:  {test_df_crash.index.min().date()} to {test_df_crash.index.max().date()} ({len(test_df_crash)} days)")

results_crash = []
for short_w, long_w, source in window_pairs:
    market_ret, strategy_ret = run_backtest(train_df_crash, short_window=short_w, long_window=long_w)
    results_crash.append({
        "Short_Window": short_w, "Long_Window": long_w, "Source": source,
        "Buy_Hold_Return": market_ret, "Strategy_Return": strategy_ret,
        "Excess_Return": strategy_ret - market_ret
    })

results_crash_df = pd.DataFrame(results_crash).sort_values("Excess_Return", ascending=False)
display_crash_df = results_crash_df.copy()
for col in ["Buy_Hold_Return", "Strategy_Return", "Excess_Return"]:
    display_crash_df[col] = display_crash_df[col].apply(lambda x: f"{x:.2%}")
print(display_crash_df.to_string(index=False))

best_short_crash, best_long_crash = 5, 20
test_market_ret_crash, test_strategy_ret_crash = run_backtest(test_df_crash, short_window=best_short_crash, long_window=best_long_crash)

print(f"\n--- [Exp 2] Out-of-Sample Test: SMA({best_short_crash}, {best_long_crash}) on 2020 Crash ---")
print(f"Buy & Hold Return (2020):  {test_market_ret_crash:.2%}")
print(f"Strategy Return (2020):    {test_strategy_ret_crash:.2%}")
print(f"Excess Return (2020):      {(test_strategy_ret_crash - test_market_ret_crash):.2%}")