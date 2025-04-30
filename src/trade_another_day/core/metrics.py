
from turtle import pd


def evaluate_performance(portfolio):
    returns = pd.Series(portfolio.history).pct_change().fillna(0)
    total_return = portfolio.history[-1] / portfolio.initial_capital - 1
    sharpe_ratio = returns.mean() / returns.std() * (252 ** 0.5)
    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")