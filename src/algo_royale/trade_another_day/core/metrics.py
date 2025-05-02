
from turtle import pd

from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION)

def evaluate_performance(portfolio):
    returns = pd.Series(portfolio.history).pct_change().fillna(0)
    total_return = portfolio.history[-1] / portfolio.initial_capital - 1
    sharpe_ratio = returns.mean() / returns.std() * (252 ** 0.5)
    logger.info(f"Total Return: {total_return:.2%}")
    logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}")