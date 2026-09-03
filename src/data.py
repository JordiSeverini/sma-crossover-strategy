# ===================================================
# data.py
# ===================================================
# Handles fetching price data from Yahoo Finance. Wrapping the download
# in a function means any analysis script can request data for whatever
# ticker/date range it needs, without repeating the yfinance call each time.

import yfinance as yf
from datetime import datetime


def get_price_data(ticker, start, end=None):

    """
    Downloads OHLCV price data for a given ticker.

    Parameters:
        ticker (str): Stock ticker symbol, e.g. "AAPL"
        start (str): Start date in "YYYY-MM-DD" format
        end (str, optional): End date in "YYYY-MM-DD" format.
                              Defaults to today if not provided.

    Returns:
        pd.DataFrame: Price data with Close, Open, High, Low, Volume columns,
                      indexed by date.
    """
    if end is None:
        end = datetime.now()

    df = yf.download(ticker, start=start, end=end, multi_level_index=False)
    return df