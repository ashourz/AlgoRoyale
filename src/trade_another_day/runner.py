## The main entry point that runs a backtest based on:
# ## strategy
# ## historical data
# ## config parameters (initial capital, fees, slippage, etc.)
# May output performance metrics, logs, and final equity curve.

"""
Entry point to run the backtest.
"""


from shared.strategies.moving_average_strategy import MovingAverageStrategy
from trade_another_day.data.data_loader import load_data
from trade_another_day.core.metrics import evaluate_performance
from trade_another_day.portfolio.portfolio import Portfolio


def run_backtest():
    data = load_data("data/BTCUSD.csv")
    strategy = MovingAverageStrategy(short_window=10, long_window=30)
    signals = strategy.generate_signals(data)

    portfolio = Portfolio(initial_capital=10000)
    portfolio.run(data, signals)

    evaluate_performance(portfolio)

if __name__ == "__main__":
    run_backtest()