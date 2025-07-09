from logging import Logger
from typing import Any, Dict

import numpy as np
import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.executor.base_backtest_executor import BacktestExecutor
from algo_royale.logging.logger_singleton import mockLogger


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
        logger: Logger,
        initial_balance: float = 1_000_000.0,
        transaction_cost: float = 0.0,
        min_lot: int = 1,
        leverage: float = 1.0,
        slippage: float = 0.0,
    ):
        self.logger = logger
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
        self.logger.info(
            f"Starting portfolio backtest for strategy: {getattr(strategy, 'get_description', lambda: str(strategy))()}"
        )

        # Validate input data
        if not self._validate_input(data):
            self.logger.error(
                "Input data validation failed for portfolio backtest. "
                "Ensure the data is a non-empty DataFrame of prices."
            )
            raise ValueError(
                "Input data validation failed for portfolio backtest. "
                "Ensure the data is a non-empty DataFrame of prices."
            )

        weights = strategy.allocate(data, data)
        self.logger.debug(
            f"Shape of data DataFrame: {data.shape}\n"
            f"Data Columns: {data.columns.tolist()}\n"
            f"Shape of weights DataFrame: {weights.shape}\n"
            f"Weights Columns: {weights.columns.tolist()}\n"
            f"Strategy weights:\n{weights.head()}\n"
            f"Initial balance: {self.initial_balance}, "
            f"Transaction cost: {self.transaction_cost}, "
            f"Minimum lot size: {self.min_lot}, "
            f"Leverage: {self.leverage}, "
            f"Slippage: {self.slippage}"
        )
        # Check that data is a DataFrame of valid prices
        if not isinstance(data, pd.DataFrame) or data.empty:
            self.logger.error(
                "Input data must be a non-empty DataFrame of prices for portfolio backtest."
            )
            raise ValueError(
                "Input data must be a non-empty DataFrame of prices for portfolio backtest."
            )
        if (data <= 0).any().any() or data.isna().any().any():
            self.logger.warning(
                "Input data contains non-positive or NaN prices. These will be skipped in trading logic."
            )
        n_steps, n_assets = data.shape
        cash = self.initial_balance
        holdings = np.zeros(n_assets)
        portfolio_values = []
        cash_history = []
        holdings_history = []
        transactions = []
        trade_id = 0
        trades_executed = 0
        self.logger.debug(f"Data shape: {data.shape}, columns: {list(data.columns)}")
        self.logger.debug(
            f"Weights shape: {weights.shape}, columns: {list(weights.columns)}"
        )
        self.logger.debug(f"Data index: {data.index[:5]} ...")
        self.logger.debug(f"Weights index: {weights.index[:5]} ...")
        for t in range(n_steps):
            target_weights = weights.iloc[t].values
            prices = data.iloc[t].values
            timestamp = data.index[t] if hasattr(data, "index") else t
            # Check for any invalid prices at this step
            if not np.all(np.isfinite(prices)) or np.any(prices <= 0):
                self.logger.warning(
                    f"Invalid prices detected at step {t}. Skipping portfolio update."
                )
                portfolio_values.append(cash + np.sum(holdings * prices))
                cash_history.append(cash)
                holdings_history.append(holdings.copy())
                continue
            total_portfolio_value = cash + np.sum(holdings * prices)
            max_investable = total_portfolio_value * self.leverage
            target_dollars = target_weights * max_investable
            current_dollars = holdings * prices
            trade_dollars = target_dollars - current_dollars
            self.logger.debug(
                f"Step {t}: cash={cash}, holdings={holdings}, prices={prices}, target_weights={target_weights}"
            )
            for i in range(n_assets):
                asset_name = data.columns[i] if hasattr(data, "columns") else str(i)
                buy_price = prices[i] * (1 + self.slippage)
                sell_price = prices[i] * (1 - self.slippage)
                # Add price checks
                if np.isnan(buy_price) or buy_price <= 0:
                    self.logger.warning(
                        f"Skipping buy for {asset_name} at step {t} due to invalid price: {buy_price}"
                    )
                    continue
                if np.isnan(sell_price) or sell_price <= 0:
                    self.logger.warning(
                        f"Skipping sell for {asset_name} at step {t} due to invalid price: {sell_price}"
                    )
                    continue

                # Validate extreme prices
                if buy_price > 1e6 or sell_price > 1e6:
                    self.logger.warning(
                        f"Skipping trade for {asset_name} at step {t} due to extreme price: buy_price={buy_price}, sell_price={sell_price}"
                    )
                    continue

                # Validate extreme quantities
                if abs(trade_dollars[i]) > 1e9:
                    self.logger.warning(
                        f"Skipping trade for {asset_name} at step {t} due to extreme trade value: trade_dollars={trade_dollars[i]}"
                    )
                    continue

                # Robustify numerical stability checks
                desired_shares = trade_dollars[i] // (
                    buy_price * (1 + self.transaction_cost)
                )
                max_affordable = (
                    cash + (self.leverage - 1) * total_portfolio_value
                ) // (buy_price * (1 + self.transaction_cost))
                if not np.isfinite(desired_shares) or desired_shares < 0:
                    self.logger.warning(
                        f"Skipping buy for {asset_name} at step {t} due to invalid desired_shares: {desired_shares}"
                    )
                    desired_shares = 0

                if not np.isfinite(max_affordable) or max_affordable < 0:
                    self.logger.warning(
                        f"Skipping buy for {asset_name} at step {t} due to invalid max_affordable: {max_affordable}"
                    )
                    max_affordable = 0

                # Ensure shares_to_buy is valid
                shares_to_buy = min(desired_shares, max_affordable)
                shares_to_buy = shares_to_buy // self.min_lot * self.min_lot
                if not np.isfinite(shares_to_buy) or shares_to_buy < 0:
                    self.logger.warning(
                        f"Skipping buy for {asset_name} at step {t} due to invalid shares_to_buy: {shares_to_buy}"
                    )
                    shares_to_buy = 0
                shares_to_buy = int(shares_to_buy)
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
                    self.logger.debug(
                        f"Buy: {shares_to_buy} of {asset_name} at {buy_price} (cost={cost})"
                    )
                    trade_id += 1
                elif trade_dollars[i] < 0:  # Sell
                    shares_to_sell = min(-trade_dollars[i] // sell_price, holdings[i])
                    # Robustify: check for NaN/inf before int conversion
                    if not np.isfinite(shares_to_sell) or shares_to_sell < 0:
                        self.logger.warning(
                            f"Skipping sell for {asset_name} at step {t} due to non-finite or negative shares_to_sell: {shares_to_sell}"
                        )
                        shares_to_sell = 0
                    shares_to_sell = shares_to_sell // self.min_lot * self.min_lot
                    if not np.isfinite(shares_to_sell) or shares_to_sell < 0:
                        self.logger.warning(
                            f"Skipping sell for {asset_name} at step {t} after lot adjustment due to non-finite or negative shares_to_sell: {shares_to_sell}"
                        )
                        shares_to_sell = 0
                    shares_to_sell = int(shares_to_sell)
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
                        self.logger.debug(
                            f"Sell: {shares_to_sell} of {asset_name} at {sell_price} (proceeds={proceeds})"
                        )
                        trade_id += 1
            portfolio_value = cash + np.sum(holdings * prices)
            portfolio_values.append(portfolio_value)
            cash_history.append(cash)
            holdings_history.append(holdings.copy())
        if trades_executed == 0:
            self.logger.warning(
                "No trades were executed during the backtest. Check input data and strategy weights."
            )
        self.logger.info(
            f"Portfolio backtest complete. Final value: {portfolio_values[-1]}, Final cash: {cash}"
        )
        results = {
            "portfolio_values": portfolio_values,
            "cash_history": cash_history,
            "holdings_history": holdings_history,
            "final_cash": cash,
            "final_holdings": holdings,
            "transactions": transactions,
        }
        # Add metrics for diagnostics and downstream use
        try:
            initial_value = self.initial_balance
            final_value = portfolio_values[-1] if portfolio_values else initial_value
            total_return = (
                (final_value / initial_value) - 1 if initial_value != 0 else np.nan
            )
            results["metrics"] = {"total_return": total_return}
        except Exception as e:
            self.logger.error(f"Error computing total_return metric: {e}")
            results["metrics"] = {}
        # Validate output data structure
        if not self._validate_output(results):
            self.logger.error(
                "Output data validation failed for portfolio backtest. "
                "Ensure the output contains the expected structure."
            )
            raise ValueError(
                "Output data validation failed for portfolio backtest. "
                "Ensure the output contains the expected structure."
            )
        return results

    def _validate_input(self, input_data: pd.DataFrame) -> bool:
        """Validate the input data structure of the backtest executor."""
        validation_method = (
            BacktestStage.PORTFOLIO_BACKTEST_EXECUTOR.value.input_validation_fn
        )
        if not validation_method:
            self.logger.warning(
                "No input validation method defined for PortfolioBacktestExecutor."
            )
            return False
        return validation_method(input_data)

    def _validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate the output data structure of the backtest executor."""
        validation_method = (
            BacktestStage.PORTFOLIO_BACKTEST_EXECUTOR.value.output_validation_fn
        )
        if not validation_method:
            self.logger.warning(
                "No output validation method defined for PortfolioBacktestExecutor."
            )
            return False
        return validation_method(output_data)


def mockPortfolioBacktestExecutor(
    initial_balance: float = 1_000_000.0,
    transaction_cost: float = 0.0,
    min_lot: int = 1,
    leverage: float = 1.0,
    slippage: float = 0.0,
) -> PortfolioBacktestExecutor:
    """
    Create a mock PortfolioBacktestExecutor for testing purposes.
    """
    return PortfolioBacktestExecutor(
        logger=mockLogger(),
        initial_balance=initial_balance,
        transaction_cost=transaction_cost,
        min_lot=min_lot,
        leverage=leverage,
        slippage=slippage,
    )
