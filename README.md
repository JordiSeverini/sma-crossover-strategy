# SMA Trading Signal Generator

A Python-based trading signal generator that uses A simple moving average crossovers on historical stock data (AAPL via yFinance) to simulate rule-based buy and sell signals.

## Overview

This project demonstrates a simple algorithmic trading strategy using technical indicators. It analyzes historical stock price data and generates signals based on short-term and long-term moving average crossovers.

## Features

- Fetches historical stock data using `yfinance`
- Calculates 20-day and 50-day simple moving averages
- Generates buy/sell signals using crossover logic
- Identifies trade entry and exit points using signal changes
- Flags whether a signal is backed by above-average trading volume

## Technologies Used

- Python
- Pandas
- NumPy
- yFinance

## Strategy Logic

- Buy signal: when the 20-day moving average crosses above the 50-day moving average
- Sell signal: when the 20-day moving average crosses below the 50-day moving average
- Volume confirmation: flags whether daily volume exceeds its 50-day rolling average, indicating stronger conviction behind a signal

## Future Improvements

- Add backtesting to evaluate strategy performance
- Visualize signals on price charts
- Extend framework to compare multiple trading strategies and evaluate performance against the moving average baseline

## Disclaimer

This project is for educational purposes only and does not constitute financial advice.
