# Does SMA Crossover Beat Buy-and-Hold?
 
A from-scratch investigation into whether a classic technical trading rule, the simple moving average (SMA) crossover, actually holds up once you stop looking at backtests and start rigorously testing whether they generalize.
 
## Why I built this
 
I started this project wanting to build a basic trading strategy: buy when a short-term moving average crosses above a long-term one, sell when it crosses back below. It's one of the first strategies anyone learns in quant finance, and it's easy to code up in an afternoon.
 
What I didn't expect was how much the project would grow once I started asking harder questions. The first version, testing SMA crossover on AAPL over a few years, showed the strategy losing badly to just buying and holding. My first instinct was that I'd picked a bad time period. So I extended the test window. Then I started wondering whether the "best" window pair I'd found was actually meaningful, or whether I'd just gotten lucky on that specific slice of history. That question turned into a proper train/test validation design. Once I had that working, I wanted to know if the result was specific to AAPL, so I added three more tickers with very different growth and volatility profiles. Along the way I added risk-adjusted metrics, realistic transaction costs, and a series of explicit "thesis checks" to verify each finding actually held up across every ticker, not just the one I happened to look at first.
 
What started as simple question  turned into a rigorous, multi-ticker, out-of-sample research project, and along the way I learned a lot about backtesting pitfalls that I don't think I would have understood nearly as well any other way.
 
## What this project actually tests
 
Using 30 years of daily price data (1996-2026) across four tickers (AAPL, SPY, DIS, KO), the project asks three questions:
 
1. **Does a window pair that looks good on historical data actually keep working on data it hasn't seen?** (Tested with two-directional train/test validation.)
2. **Is there a stable "best" window pair for a given stock, or does the answer change depending on which years you look at?** (Tested by comparing the winning window from two different training periods.)
3. **Even if the strategy doesn't beat buy-and-hold on raw return, does it at least protect against the worst losses?** (Tested with Max Drawdown, across every window pair tested.)
## Key findings
 
- **Buy-and-hold won on raw return in every single test**, including a full 30-year hindsight comparison with no restrictions on foresight, for three of the four tickers.
- **The "best" window pair consistently failed to generalize.** Across 8 independent train/test trials, only 3 showed a genuine in-sample edge, and none of those edges survived out-of-sample testing.
- **There is no stable "optimal" window.** For every ticker tested, the best-performing short/long window pair shifted substantially depending on which historical period was used to find it.
- **Drawdown protection is real, but inconsistent.** SMA crossover meaningfully reduced worst-case losses for three of four tickers, but this benefit reversed for long-lag windows on AAPL and was almost entirely absent for KO.
- Part of this comes down to a structural limitation: SMA crossover always trades one day behind its own signal, so it's inherently reactive. Part of it comes down to timing: the 30-year test period includes an unusually long, strong bull market, an environment where any strategy that periodically exits the market gives up compounding it rarely gets back.
The full methodology, all four tickers' results, and the complete set of visuals are here ([PDF](Report/Technical_report.pdf)).
 
## Project structure
 
```
sma-crossover-strategy/
├── analysis/
│   └── main_analysis.py           # Runs the full experiment suite across all 4 tickers
├── outputs/
│   ├── figures/                    # Generated chart images
│   └── all_results.pkl             # Saved results, loaded by chart scripts
├── Report/
│   └── Technical_report.pdf        # PDF export of the report
├── src/
│   ├── Thesis_checks/               # Overfitting, parameter instability, drawdown checks
│   ├── backtest.py                  # Core SMA crossover engine, Sharpe Ratio, Max Drawdown
│   ├── data.py                      # Price data fetching (yfinance)
│   └── run_experiments.py           # Train/test + hindsight experiment runner
├── visuals/
│   ├── all_tickers_equity_curve.py  # 2x2 grid: buy & hold vs best strategy, per ticker
│   ├── drawdown_chart.py
│   ├── equity_curve.py               # AAPL-specific equity curve
│   ├── instability_chart.py
│   ├── overfitting_chart.py
│   └── sharpe_chart.py
└── README.md
```
 
## How to run it
 
This assumes you've cloned the repository to your own machine and are running commands from a terminal, inside the project's root folder.
 
```bash
git clone https://github.com/<your-username>/sma-crossover-strategy.git
cd sma-crossover-strategy
 
pip install yfinance pandas numpy matplotlib
 
python analysis/main_analysis.py
```
 
This downloads 30 years of daily price data for AAPL, SPY, DIS, and KO, runs the full grid search and train/test validation for each, and saves results to `outputs/all_results.pkl` for the visual scripts to use.
 
To regenerate the charts (fast, loads from the saved results rather than re-running the analysis):
 
```bash
python visuals/overfitting_chart.py
python visuals/instability_chart.py
python visuals/drawdown_chart.py
python visuals/sharpe_chart.py
python visuals/equity_curve.py
python visuals/all_tickers_equity_curve.py
```
