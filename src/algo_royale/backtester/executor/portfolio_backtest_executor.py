from typing import Any, Dict

import numpy as np
import pandas as pd

from algo_royale.backtester.executor.base_backtest_executor import BacktestExecutor


class PortfolioBacktestExecutor(BacktestExecutor):
    """
    Executes a portfolio strategy over a DataFrame of returns/signals and produces portfolio results.
    Simulates cash constraints, partial fills, transaction costs, minimum lot size, and leverage.
    Parameters:
        : initial_balance: Initial cash balance for the portfolio.
        : transaction_cost: Transaction cost as a fraction of the trade value (0.0 for no cost, 0.001 for 0.1%).
            It simulates real-world brokerage fees, commissions, or other costs associated with executing trades.
            This cost is applied to both buy and sell transactions, reducing the effective amount of cash available for trading.
        : min_lot: Minimum lot size for trades (e.g., 1 for fractional shares, 100 for round lots).
        : leverage: Leverage factor (1.0 for no leverage, >1.0 for margin trading).
        : slippage: Slippage factor as a fraction of the price (0.0 for no slippage).
    """

    def __init__(
        self,
        initial_balance: float = 1_000_000.0,
        transaction_cost: float = 0.0,
        min_lot: int = 1,
        leverage: float = 1.0,
        slippage: float = 0.0,
    ):
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.min_lot = max(1, int(min_lot))
        self.leverage = leverage
        self.slippage = slippage

    def run_backtest(
        self,
        strategy,
        data: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Run a backtest for the given strategy and data.
        Parameters:
            : strategy: Portfolio strategy instance implementing allocation logic.
            : data: DataFrame containing asset prices or returns/signals.
        Returns:
            : Dictionary containing portfolio values, cash history, holdings history, and transactions.
        """
        weights = strategy.allocate(data, data)
        n_steps, n_assets = data.shape
        cash = self.initial_balance
        holdings = np.zeros(n_assets)
        portfolio_values = []
        cash_history = []
        holdings_history = []
        transactions = []
        trade_id = 0
        for t in range(n_steps):
            target_weights = weights.iloc[t].values
            prices = data.iloc[t].values
            timestamp = data.index[t] if hasattr(data, "index") else t
            total_portfolio_value = cash + np.sum(holdings * prices)
            max_investable = total_portfolio_value * self.leverage
            target_dollars = target_weights * max_investable
            current_dollars = holdings * prices
            trade_dollars = target_dollars - current_dollars
            for i in range(n_assets):
                asset_name = data.columns[i] if hasattr(data, "columns") else str(i)
                buy_price = prices[i] * (1 + self.slippage)
                sell_price = prices[i] * (1 - self.slippage)
                if trade_dollars[i] > 0:  # Buy
                    max_affordable = (
                        cash + (self.leverage - 1) * total_portfolio_value
                    ) // (buy_price * (1 + self.transaction_cost))
                    desired_shares = trade_dollars[i] // (
                        buy_price * (1 + self.transaction_cost)
                    )
                    shares_to_buy = min(desired_shares, max_affordable)
                    shares_to_buy = int(shares_to_buy // self.min_lot * self.min_lot)
                    cost = shares_to_buy * buy_price * (1 + self.transaction_cost)
                    if (
                        shares_to_buy > 0
                        and cost <= cash + (self.leverage - 1) * total_portfolio_value
                    ):
                        holdings[i] += shares_to_buy
                        cash -= cost
                        transactions.append(
                            {
                                "trade_id": trade_id,
                                "timestamp": str(timestamp),
                                "step": t,
                                "asset": asset_name,
                                "action": "buy",
                                "quantity": int(shares_to_buy),
                                "price": float(buy_price),
                                "cost": float(cost),
                                "cash_after": float(cash),
                                "holdings_after": float(holdings[i]),
                            }
                        )
                        trade_id += 1
                elif trade_dollars[i] < 0:  # Sell
                    shares_to_sell = min(-trade_dollars[i] // sell_price, holdings[i])
                    shares_to_sell = int(shares_to_sell // self.min_lot * self.min_lot)
                    proceeds = shares_to_sell * sell_price * (1 - self.transaction_cost)
                    if shares_to_sell > 0:
                        holdings[i] -= shares_to_sell
                        cash += proceeds
                        transactions.append(
                            {
                                "trade_id": trade_id,
                                "timestamp": str(timestamp),
                                "step": t,
                                "asset": asset_name,
                                "action": "sell",
                                "quantity": int(shares_to_sell),
                                "price": float(sell_price),
                                "proceeds": float(proceeds),
                                "cash_after": float(cash),
                                "holdings_after": float(holdings[i]),
                            }
                        )
                        trade_id += 1
            portfolio_value = cash + np.sum(holdings * prices)
            portfolio_values.append(portfolio_value)
            cash_history.append(cash)
            holdings_history.append(holdings.copy())
        results = {
            "portfolio_values": portfolio_values,
            "cash_history": cash_history,
            "holdings_history": holdings_history,
            "final_cash": cash,
            "final_holdings": holdings,
            "transactions": transactions,
        }
        return results
