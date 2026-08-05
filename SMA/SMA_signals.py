# IMPORT LIBRARIES #
#############################################
# yfinance is python library that provides a convenient wrapper around Yahoo Finance's data allowing you to fetch real time data 
import yfinance as yf 
import pandas as pd 
import numpy as np 
from datetime import datetime

Ticker = "AAPL"

# DOWNLOAD DATA #
#############################################
# yfinance wraps the information into a pandas dataframe with OHLCV (Open, High, Low, Close, Volume)
df = yf.download(Ticker, start="2025-01-01", end=datetime.now(), multi_level_index=False)


# CREATE SIMPLE MOVING AVERAGES (SMA) #
#############################################
# creates new columns "SMA_SHORT" "SMA_LONG"
# pandas methods
    # .rolling() groups data into chunks of a fixed size and moves that chunk one row at a time down the DataFrame.
    # .mean() calculates the mean of the window
df["SMA_SHORT"] = df["Close"].rolling(window=20).mean()
df["SMA_LONG"] = df["Close"].rolling(window=50).mean()


# GENERATE BUY/SELL SIGNALS #
#############################################
# Create a new column "Signal" and initialize every value to 0
df["Signal"] = 0

# np.where() is from numpy and works like an if/else for an entire column at once
# If "SMA_SHORT" > "SMA_LONG" -> put 1 (Short term trend is rising, bullish)
# Otherwise -> put 0 (Short term trend is falling, bearish)
df["Signal"] = np.where(df["SMA_SHORT"] > df["SMA_LONG"], 1, 0)


# BUY/SELL LABELS #
#############################################
# .diff() subtracts the previous row from the current row
# it detects where the Signal changed
    # current(1) - previous(0) = 1 (BUY)
    # current(0) - previous(1) = -1 (SELL)
    # 0 means no change
# .map() converts the numeric diff into a readable label
df["Position"] = df["Signal"].diff().map({1: "BUY", -1: "SELL", 0: "HOLD"})


# VOLUME CONFIRMATION #
#############################################
# Creates a Volume average column with the rolling average over 50 days
df["Volume_AVG"] = df["Volume"].rolling(window=50).mean()

# Flags whether volume was above its 50-day average on a given day
# Used to check if a Signal change (Position) is backed by strong volume
df["Volume_Conf"] = np.where(df["Volume"] > df["Volume_AVG"], 1, 0)


# FILTER & FORMAT OUTPUT #
#############################################
# filters the df (dataframe) to only keep certain columns, in order
df = df[["Close", "SMA_SHORT", "SMA_LONG", "Volume", "Volume_AVG", "Signal", "Volume_Conf", "Position"]]

# .to_string() is a method that explicitly renders the DataFrame as a formatted string, and unlike 
# the default representation, it accepts extra arguments to control how that string gets built
# formatters: a dict where each key is a column name, and each value is a
# function that takes one value from that column and returns a formatted string
print(df.tail().to_string(formatters={
    "Volume_AVG": "{:,}".format,
    "Volume": "{:,}".format,
}))

