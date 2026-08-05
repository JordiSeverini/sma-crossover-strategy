# IMPORT LIBRARIES #
#############################################
# yfinance is python library that provides a convenient wrapper around Yahoo Finance's data allowing you to fetch real time data 
import yfinance as yf 
import pandas as pd 
import numpy as np 
import matplotlib as plt

# yfinance wraps the information into a pandas dataframe with OHLCV (Open, High, Low, Close, Volume)
df = yf.download("AAPL",start = "2020-01-01", end  = "2024-01-01")

# filters the df (dataframe) to only keep the close column
# df = df[["Close"]]

# Prints the tail (Default Last 5 rows)
print(df.tail())


# CREATE SIMPLE MaOVING AVERAGES (SMA) #
#######################################
# creates new rows "SMA_SHORT" "SMA_LONG"
# pandas methods
    # .rolling() groups data into chunks of a fixed size and moves that chunk one row at a time down the DataFrame.
    # .mean() calculates the mean of the window
df["SMA_SHORT"] = df["Close"].rolling(window = 20).mean()
df["SMA_LONG"] = df["Close"].rolling(window = 50).mean()

# GENERATE BUY/SELL SIGNALS #
#######################################
# Create a new row "Signal" and initalize every column value to 0
df["Signal"] = 0

# np.where() is from numpy and works like an if/else for an entire column at once
# If "SMA_SHORT" > "SMA_LONG" -> put 1 (Short term trend is rising, bullish)
# Otherwise -> put 0 (Short term trend is falling, bearish)
df["Signal"] = np.where(df["SMA_SHORT"] > df["SMA_LONG"], 1, 0)


# Creates a new Position row 
# .diff() subtracts the previous row from the current row
#  it detects where the Signal changed
    # 1 means Signal just changed from prev(0) - current(1) = (BUY)
    # -1 means Signal just changed from prev(1) -> current(0) = (SELL)
    # 0 means no change
df["Position"] = df["Signal"].diff()






