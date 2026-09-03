# ===================================================
# backtest.py
# ===================================================
# Core reusable strategy-testing functions. This file has no data-download
# logic and no experiment-running logic -- just the engine that any
# analysis script can import and use.

import pandas as pd
import numpy as np


# ===================================================
# BACKTEST FUNCTION #
# ===================================================
# Wraps the whole SMA crossover strategy into a reusable function, to
# call it repeatedly with different short/long window values 
def run_backtest(price_df, short_window, long_window, transaction_cost_pct=0.001):
    df = price_df.copy()  # work on a copy

    # ===================================================
    # CREATE SIMPLE MOVING AVERAGES (SMA) #
    # ===================================================
    # .rolling() groups data into chunks of a fixed size and moves that chunk one row at a time down the DataFrame.
    # .mean() calculates the mean of the window
    df["SMA_SHORT"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_LONG"] = df["Close"].rolling(window=long_window).mean()

    # ===================================================
    # GENERATE BUY/SELL SIGNALS #
    # ===================================================
    # If "SMA_SHORT" > "SMA_LONG" -> put 1 (Short term trend is rising, bullish)
    # Otherwise -> put 0 (Short term trend is falling, bearish)
    df["Signal"] = np.where(df["SMA_SHORT"] > df["SMA_LONG"], 1, 0)

    # The first x - 1 days at the beginning of the simulation are NaN
    # (SMA_LONG needs x rows of data before it can compute a real average)
    # This finds the rows where SMA_LONG is NaN, then sets Signal to NaN in those same rows
    df.loc[df["SMA_LONG"].isna(), "Signal"] = np.nan

    # ===================================================
    # BUY/SELL LABELS #
    # ===================================================
    # .diff() detects where the Signal changed:
    # current(1) - previous(0) = 1 (BUY)
    # current(0) - previous(1) = -1 (SELL)
    # 0 = no change
    df["Position"] = df["Signal"].diff().map({1: "BUY", -1: "SELL", 0: "HOLD"})

    # Prevents false position signal from NaN -> real data (during warm up)
    df.loc[df["SMA_LONG"].isna(), "Position"] = None

    # ===================================================
    # MARKET & STRATEGY RETURNS #
    # ===================================================
    # Market Return = today's close vs yesterday's close
    df["Market_Return"] = df["Close"].pct_change()

    # What the strategy captured each day -- uses YESTERDAY's signal, since
    # you can't act on today's signal until today has already closed
    df["Strategy_Return"] = df["Market_Return"] * df["Signal"].shift(1)

    # ===================================================
    # TRANSACTION COSTS #
    # ===================================================
    # Every time Signal flips (a BUY or SELL), a real trade happens -- and real
    # trades cost money (commission + slippage). We model this as a fixed
    # percentage cost applied on each trade day, which reduces that day's return.
    # A trade occurred whenever Signal changed from the previous day (non-zero diff)
    trade_occurred = df["Signal"].diff().abs() > 0

    
    # NOTE TO SELF: what this line actually does

    # df.loc[trade_occurred, "Strategy_Return"] = df.loc[trade_occurred, "Strategy_Return"] - transaction_cost_pct
    #
    # trade_occurred = a True/False mask, True only on days a trade happened
    #
    # RIGHT side: reads the CURRENT Strategy_Return values, but only on trade days,
    #             then subtracts the cost from them
    # LEFT side:  writes those new (cost-adjusted) values back into Strategy_Return,
    #             again only on those same trade days
    # Net effect: on HOLD days, nothing changes. On trade days, Strategy_Return
    # gets reduced by transaction_cost_pct (e.g. 0.001 = 0.1%) to reflect the
    # real cost of commission + slippage from actually placing that trade.

    df.loc[trade_occurred, "Strategy_Return"] = df.loc[trade_occurred, "Strategy_Return"] - transaction_cost_pct



    # ===================================================
    # CUMULATIVE RETURNS #
    # ===================================================
    # Compounds daily returns into a running $1 return
    # e.g. if Cumulative_Market = 1.15, that means $1 invested at the start
    # would be worth $1.15 by that date (a 15% total return so far)
    df["Cumulative_Market"] = (1 + df["Market_Return"]).cumprod()
    df["Cumulative_Strategy"] = (1 + df["Strategy_Return"]).cumprod()

     # ===================================================
        # MAX DRAWDOWN #
        # ===================================================
        # Max Drawdown = the largest peak-to-trough decline in cumulative value.
        # Answers: "what's the worst loss I'd have experienced if I'd bought at the
        # best possible moment and held through to the worst point after it?"
    def calculate_max_drawdown(cumulative_series):
            running_max = cumulative_series.cummax()
            drawdown = (cumulative_series - running_max) / running_max
            return drawdown.min()
    
    strategy_max_dd = calculate_max_drawdown(df["Cumulative_Strategy"])
    market_max_dd = calculate_max_drawdown(df["Cumulative_Market"])

    # ===================================================
    # TOTAL RETURN SUMMARY #
    # ===================================================
    total_market_return = df["Cumulative_Market"].iloc[-1] - 1
    total_strategy_return = df["Cumulative_Strategy"].iloc[-1] - 1

        # SHARPE RATIO #
    # ===================================================
    # Sharpe Ratio = (average daily return / standard deviation of daily returns) * sqrt(252)
    # Answers: "how much return am I getting per unit of risk taken?"
    # The sqrt(252) annualizes it, since there are ~252 trading days in a year.
    strategy_sharpe = (
        df["Strategy_Return"].mean() / df["Strategy_Return"].std() * np.sqrt(252)
        if df["Strategy_Return"].std() != 0 else np.nan
    )
    market_sharpe = (
        df["Market_Return"].mean() / df["Market_Return"].std() * np.sqrt(252)
        if df["Market_Return"].std() != 0 else np.nan
    )

   

    return total_market_return, total_strategy_return, market_sharpe, strategy_sharpe, market_max_dd,strategy_max_dd


# ===================================================
# GRID SEARCH FUNCTION #
# ===================================================
# Runs run_backtest() across every window pair against a given training
# DataFrame, and returns a sorted results table -- avoids rewriting this
# loop every time testing a new training period.
def run_grid_search(dataframe, pairs, transaction_cost_pct = 0.001):
    results = []
    for short_w, long_w in pairs:
        market_ret, strategy_ret, market_sharpe, strategy_sharpe, market_max_dd, strategy_max_dd = run_backtest(dataframe, short_window=short_w, long_window=long_w, transaction_cost_pct = transaction_cost_pct)
        results.append({
            "Short_Window": short_w,
            "Long_Window": long_w,
            "Buy_Hold_Return": market_ret,
            "Strategy_Return": strategy_ret,
            "Excess_Return": strategy_ret - market_ret,
            "Buy_&_Hold_Sharpe": market_sharpe,
            "Strategy_Sharpe" : strategy_sharpe,
            "Market_max_dd" : market_max_dd,
            "Strategy_max_dd" : strategy_max_dd
        })
    results_df = pd.DataFrame(results).sort_values("Excess_Return", ascending=False)
    return results_df


# Small helper to print a results table with percentage formatting
def display_results(results_df, label):
    display_df = results_df.copy()
    for col in ["Buy_Hold_Return", "Strategy_Return", "Excess_Return","Market_max_dd", "Strategy_max_dd"]:
        display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")
    for col in ["Buy_&_Hold_Sharpe", "Strategy_Sharpe"]:
        display_df[col] = display_df[col].apply(lambda x : f"{x:.2f}")
    print(f"\n--- {label} ---")
    print(display_df.to_string(index=False))