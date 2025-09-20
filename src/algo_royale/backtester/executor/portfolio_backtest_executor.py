from typing import Any, Dict

import numpy as np
import pandas as pd

from algo_royale.backtester.column_names.portfolio_execution_keys import (
    PortfolioExecutionKeys,
    PortfolioExecutionMetricsKeys,
)
from algo_royale.backtester.column_names.portfolio_transaction_keys import (
    PortfolioTransactionKeys,
)
from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)
from algo_royale.logging.loggable import Loggable


class PortfolioBacktestExecutor:
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
        logger: Loggable,
        initial_balance: float = 1_000_000.0,
        transaction_cost: float = 0.0,
        min_lot: int = 1,
        leverage: float = 1.0,
        slippage: float = 0.0,
        settlement_days: int = 1,
    ):
        self.logger = logger
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.min_lot = max(1, int(min_lot))
        self.leverage = leverage
        self.slippage = slippage
        self.settlement_days = int(settlement_days)

    def async_run_backtest(
        self,
        strategy: BasePortfolioStrategy,
        data: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Run a backtest for the given strategy and data, with robust validation, error handling, and detailed logging.
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

        # Forward-fill missing values so each symbol's value remains until new data arrives
        data = data.ffill()

        try:
            weights = strategy.allocate(data, data)
        except Exception as e:
            self.logger.error(f"Error in strategy.allocate: {e}")
            raise

        self.logger.debug(
            f"Shape of data DataFrame: {data.shape}\n"
            f"Data Columns: {getattr(data, 'columns', [])}\n"
            f"Shape of weights DataFrame: {getattr(weights, 'shape', None)}\n"
            f"Weights Columns: {getattr(weights, 'columns', [])}\n"
            f"Strategy weights (head):\n{getattr(weights, 'head', lambda: None)()}\n"
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
        # Settlement logic: track pending settlements as list of dicts {amount, settle_step}
        pending_settlements = []

        self.logger.debug(f"Data shape: {data.shape}, columns: {list(data.columns)}")
        self.logger.debug(
            f"Weights shape: {weights.shape}, columns: {list(weights.columns)}"
        )
        self.logger.debug(f"Data index: {data.index[:5]} ...")
        self.logger.debug(f"Weights index: {weights.index[:5]} ...")

        for t in range(n_steps):
            # Release any settled cash
            released_cash = 0.0
            if self.settlement_days > 0:
                # Find all settlements that are due
                still_pending = []
                for s in pending_settlements:
                    if s["settle_step"] <= t:
                        released_cash += s["amount"]
                    else:
                        still_pending.append(s)
                if released_cash > 0:
                    self.logger.debug(
                        f"[{t}] Released ${released_cash} from settlement queue."
                    )
                pending_settlements = still_pending
                cash += released_cash

            target_weights = weights.iloc[t].values
            prices = data.iloc[t].values
            timestamp = data.index[t] if hasattr(data, "index") else t
            # Identify valid and invalid assets at this step
            valid_mask = np.isfinite(prices) & (prices > 0) & (prices <= 1e6)
            invalid_assets = [
                data.columns[i] if hasattr(data, "columns") else str(i)
                for i, valid in enumerate(valid_mask)
                if not valid
            ]
            if invalid_assets:
                self.logger.warning(
                    f"[{timestamp}] Invalid prices detected at step {t} for assets: {invalid_assets}. Skipping these assets for this step."
                )
            # For invalid assets, set their weights and prices to zero for this step
            step_target_weights = target_weights.copy()
            step_prices = prices.copy()
            step_target_weights[~valid_mask] = 0.0
            step_prices[~valid_mask] = 0.0

            total_portfolio_value = cash + np.sum(holdings * step_prices)
            max_investable = total_portfolio_value * self.leverage
            target_dollars = step_target_weights * max_investable
            current_dollars = holdings * step_prices
            trade_dollars = target_dollars - current_dollars
            self.logger.debug(
                f"[{timestamp}] Step {t}: cash={cash}, holdings={holdings}, prices={step_prices}, target_weights={step_target_weights}"
            )
            # Cap extreme quantities and costs
            max_quantity = 1e9
            max_cost = 1e12

            for i in range(n_assets):
                if not valid_mask[i]:
                    continue  # skip trading for invalid asset
                asset_name = data.columns[i] if hasattr(data, "columns") else str(i)
                buy_price = step_prices[i] * (1 + self.slippage)
                sell_price = step_prices[i] * (1 - self.slippage)

                if buy_price > 1e6 or sell_price > 1e6:
                    self.logger.warning(
                        f"[{timestamp}] Skipping trade for {asset_name} at step {t} due to extreme price: buy_price={buy_price}, sell_price={sell_price} (value: {step_prices[i]})"
                    )
                    continue

                trade_dollars[i] = min(trade_dollars[i], max_cost)

                # Only attempt buy if trade_dollars[i] is strictly positive and above a small epsilon
                if trade_dollars[i] > 1e-8:
                    denom = buy_price * (1 + self.transaction_cost)
                    if denom <= 0 or not np.isfinite(denom):
                        self.logger.warning(
                            f"[{timestamp}] Skipping buy for {asset_name} at step {t} due to invalid denominator: {denom}. (price: {step_prices[i]})"
                        )
                        continue
                    desired_shares = trade_dollars[i] // denom
                    desired_shares = min(desired_shares, max_quantity)

                    # Only proceed if desired_shares is strictly positive and finite
                    if not np.isfinite(desired_shares) or desired_shares <= 0:
                        self.logger.warning(
                            f"[{timestamp}] Skipping buy for {asset_name} at step {t} due to non-positive or invalid desired_shares: {desired_shares}. trade_dollars[i]: {trade_dollars[i]}, buy_price: {buy_price}, transaction_cost: {self.transaction_cost}, price: {step_prices[i]}"
                        )
                        continue

                    shares_to_buy = min(desired_shares, max_quantity)
                    shares_to_buy = shares_to_buy // self.min_lot * self.min_lot
                    if not np.isfinite(shares_to_buy) or shares_to_buy <= 0:
                        self.logger.warning(
                            f"[{timestamp}] Skipping buy for {asset_name} at step {t} due to non-positive or invalid shares_to_buy: {shares_to_buy}. desired_shares: {desired_shares}, max_quantity: {max_quantity}, min_lot: {self.min_lot}, price: {step_prices[i]}"
                        )
                        continue

                    # Ensure numerical stability
                    cost = shares_to_buy * buy_price * (1 + self.transaction_cost)
                    if cost > max_cost:
                        self.logger.warning(
                            f"[{timestamp}] Skipping buy for {asset_name} at step {t} due to excessive cost: {cost} (price: {step_prices[i]})"
                        )
                        continue

                    # Only use settled cash for buys
                    available_cash = cash
                    if self.settlement_days > 0:
                        available_cash = cash
                    if (
                        shares_to_buy > 0
                        and cost
                        <= available_cash + (self.leverage - 1) * total_portfolio_value
                    ):
                        holdings[i] += shares_to_buy
                        cash -= cost
                        transactions.append(
                            {
                                PortfolioTransactionKeys.TRADE_ID: trade_id,
                                PortfolioTransactionKeys.TIMESTAMP: str(timestamp),
                                PortfolioTransactionKeys.STEP: t,
                                PortfolioTransactionKeys.ASSET: asset_name,
                                PortfolioTransactionKeys.ACTION: "buy",
                                PortfolioTransactionKeys.QUANTITY: int(shares_to_buy),
                                PortfolioTransactionKeys.PRICE: float(buy_price),
                                PortfolioTransactionKeys.COST: float(cost),
                                PortfolioTransactionKeys.CASH_AFTER: float(cash),
                                PortfolioTransactionKeys.HOLDINGS_AFTER: float(
                                    holdings[i]
                                ),
                            }
                        )
                        self.logger.debug(
                            f"[{timestamp}] Buy: {shares_to_buy} of {asset_name} at {buy_price} (cost={cost})"
                        )
                        trade_id += 1
                        trades_executed += 1
                elif trade_dollars[i] < 0:  # Sell
                    shares_to_sell = min(-trade_dollars[i] // sell_price, holdings[i])
                    # Robustify: check for NaN/inf before int conversion
                    if not np.isfinite(shares_to_sell) or shares_to_sell < 0:
                        self.logger.warning(
                            f"[{timestamp}] Skipping sell for {asset_name} at step {t} due to non-finite or negative shares_to_sell: {shares_to_sell} (price: {step_prices[i]})"
                        )
                        shares_to_sell = 0
                    shares_to_sell = shares_to_sell // self.min_lot * self.min_lot
                    if not np.isfinite(shares_to_sell) or shares_to_sell < 0:
                        self.logger.warning(
                            f"[{timestamp}] Skipping sell for {asset_name} at step {t} after lot adjustment due to non-finite or negative shares_to_sell: {shares_to_sell} (price: {step_prices[i]})"
                        )
                        shares_to_sell = 0
                    shares_to_sell = int(shares_to_sell)
                    proceeds = shares_to_sell * sell_price * (1 - self.transaction_cost)
                    if shares_to_sell > 0:
                        holdings[i] -= shares_to_sell
                        # Instead of immediately adding proceeds to cash, add to pending settlements
                        if self.settlement_days > 0:
                            pending_settlements.append(
                                {
                                    "amount": proceeds,
                                    "settle_step": t + self.settlement_days,
                                }
                            )
                            self.logger.debug(
                                f"[{timestamp}] Sell: {shares_to_sell} of {asset_name} at {sell_price} (proceeds={proceeds}) - proceeds pending settlement at step {t + self.settlement_days}"
                            )
                        else:
                            cash += proceeds
                        transactions.append(
                            {
                                PortfolioTransactionKeys.TRADE_ID: trade_id,
                                PortfolioTransactionKeys.TIMESTAMP: str(timestamp),
                                PortfolioTransactionKeys.STEP: t,
                                PortfolioTransactionKeys.ASSET: asset_name,
                                PortfolioTransactionKeys.ACTION: "sell",
                                PortfolioTransactionKeys.QUANTITY: int(shares_to_sell),
                                PortfolioTransactionKeys.PRICE: float(sell_price),
                                PortfolioTransactionKeys.PROCEEDS: float(proceeds),
                                PortfolioTransactionKeys.CASH_AFTER: float(cash),
                                PortfolioTransactionKeys.HOLDINGS_AFTER: float(
                                    holdings[i]
                                ),
                            }
                        )
                        trade_id += 1
                        trades_executed += 1
            # Only include valid prices/holdings in portfolio value calculation
            valid_for_value = np.isfinite(prices) & (prices > 0) & np.isfinite(holdings)
            portfolio_value = cash + np.sum(
                holdings[valid_for_value] * prices[valid_for_value]
            )
            portfolio_values.append(portfolio_value)
            self.logger.debug(
                f"[{timestamp}] Step {t}: portfolio_value={portfolio_value}, cash={cash}, holdings={holdings}, prices={prices}"
            )
            if not np.isfinite(portfolio_value):
                self.logger.warning(
                    f"[{timestamp}] Step {t}: NaN or inf in portfolio_value! cash={cash}, holdings={holdings}, prices={prices}"
                )
            if not np.all(np.isfinite(prices)):
                non_finite_info = [
                    f"{data.columns[i]}={prices[i]}"
                    for i in range(len(prices))
                    if not np.isfinite(prices[i])
                ]
                self.logger.warning(
                    f"[{timestamp}] Step {t}: Non-finite prices detected for: {', '.join(non_finite_info)}"
                )
            if not np.all(np.isfinite(holdings)):
                self.logger.warning(
                    f"[{timestamp}] Step {t}: Non-finite holdings detected: {holdings}"
                )
            cash_history.append(cash)
            holdings_history.append(holdings.copy())

        if trades_executed == 0:
            self.logger.warning(
                f"[{timestamp}] No trades were executed during the backtest. This may indicate that the strategy weights, price data, or constraints prevented any trades. "
                f"[{timestamp}] Input data shape: {data.shape}, Weights shape: {weights.shape}, Initial balance: {self.initial_balance}, Transaction cost: {self.transaction_cost}, Min lot: {self.min_lot}, Leverage: {self.leverage}, Slippage: {self.slippage}"
            )
            # Optionally, add a flag to results for downstream logic

        # Defensive: ensure portfolio_values is not empty
        if not portfolio_values:
            self.logger.error(
                f"[{timestamp}] No portfolio values were generated during the backtest. Returning empty result structure."
            )
            results = {
                PortfolioExecutionKeys.PORTFOLIO_VALUES: [],
                PortfolioExecutionKeys.CASH_HISTORY: [],
                PortfolioExecutionKeys.HOLDINGS_HISTORY: [],
                PortfolioExecutionKeys.FINAL_CASH: cash,
                PortfolioExecutionKeys.FINAL_HOLDINGS: holdings,
                PortfolioExecutionKeys.TRANSACTIONS: [],
                PortfolioExecutionKeys.METRICS: {
                    PortfolioExecutionMetricsKeys.TOTAL_RETURN: np.nan,
                    PortfolioExecutionMetricsKeys.ERROR: "No portfolio values generated",
                },
                PortfolioExecutionKeys.EMPTY_RESULT: True,
            }
            return results

        self.logger.info(
            f"[{timestamp}] Portfolio backtest complete. Final value: {portfolio_values[-1]}, Final cash: {cash}"
        )
        # Log portfolio_values for diagnostics
        try:
            pv_arr = np.array(portfolio_values)
            self.logger.debug(f"portfolio_values (head): {pv_arr[:10]}")
            self.logger.debug(f"portfolio_values (tail): {pv_arr[-10:]}")
            self.logger.debug(f"portfolio_values NaN count: {np.isnan(pv_arr).sum()}")
        except Exception as e:
            self.logger.error(f"Error logging portfolio_values diagnostics: {e}")
        results = {
            PortfolioExecutionKeys.PORTFOLIO_VALUES: portfolio_values,
            PortfolioExecutionKeys.CASH_HISTORY: cash_history,
            PortfolioExecutionKeys.HOLDINGS_HISTORY: holdings_history,
            PortfolioExecutionKeys.FINAL_CASH: cash,
            PortfolioExecutionKeys.FINAL_HOLDINGS: holdings,
            PortfolioExecutionKeys.TRANSACTIONS: transactions,
        }
        self.logger.debug(
            f"Backtest results keys: {list(results.keys())}, "
            f"portfolio_values len: {len(portfolio_values)}, "
            f"transactions len: {len(transactions)}"
        )

        # Add DataFrame versions for manual review and downstream analysis
        results[PortfolioExecutionKeys.TRANSACTIONS_DF] = (
            pd.DataFrame(transactions) if transactions else pd.DataFrame()
        )
        results[PortfolioExecutionKeys.PORTFOLIO_VALUES_DF] = (
            pd.DataFrame({"portfolio_value": portfolio_values})
            if portfolio_values
            else pd.DataFrame()
        )

        # Add metrics for diagnostics and downstream use
        try:
            initial_value = self.initial_balance
            final_value = portfolio_values[-1] if portfolio_values else initial_value
            total_return = (
                (final_value / initial_value) - 1 if initial_value != 0 else np.nan
            )
            # Compute per-period (stepwise) returns
            if len(portfolio_values) > 1:
                pv_arr = np.array(portfolio_values)
                portfolio_returns = (pv_arr[1:] / pv_arr[:-1]) - 1
                portfolio_returns = portfolio_returns.tolist()
                # Prepend 0.0 so returns aligns with values
                portfolio_returns = [0.0] + portfolio_returns
            else:
                portfolio_returns = []
            results[PortfolioExecutionKeys.METRICS] = {
                PortfolioExecutionMetricsKeys.TOTAL_RETURN: total_return,
                PortfolioExecutionMetricsKeys.PORTFOLIO_RETURNS: portfolio_returns,
            }
        except Exception as e:
            self.logger.error(
                f"Error computing total_return or portfolio_returns metric: {e}"
            )
            results[PortfolioExecutionKeys.METRICS] = {
                PortfolioExecutionMetricsKeys.TOTAL_RETURN: np.nan,
                PortfolioExecutionMetricsKeys.PORTFOLIO_RETURNS: [],
                PortfolioExecutionMetricsKeys.ERROR: str(e),
            }

        # Validate output data structure
        if not self._validate_output(results):
            self.logger.error(
                "Output data validation failed for portfolio backtest. "
                "Ensure the output contains the expected structure."
            )
            results[PortfolioExecutionKeys.METRICS][
                PortfolioExecutionMetricsKeys.ERROR
            ] = "Output data validation failed"
            results[PortfolioExecutionKeys.INVALID_OUTPUT] = True
            # Optionally, raise or just return the flagged result
            # raise ValueError(
            #     "Output data validation failed for portfolio backtest. "
            #     "Ensure the output contains the expected structure."
            # )
        # self.logger.info(f"Backtest results: {results}")
        return results

    def _validate_input(self, input_data: pd.DataFrame) -> bool:
        """Validate the input data structure of the backtest executor."""
        try:
            validation_method = (
                BacktestStage.PORTFOLIO_BACKTEST_EXECUTOR.value.input_validation_fn
            )
            if not validation_method:
                self.logger.warning(
                    "No input validation method defined for PortfolioBacktestExecutor."
                )
                return False
            return validation_method(input_data, self.logger)
        except Exception as e:
            self.logger.error(
                f"Error validating input data for PortfolioBacktestExecutor: {e}"
            )
            return False

    def _validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate the output data structure of the backtest executor."""
        try:
            validation_method = (
                BacktestStage.PORTFOLIO_BACKTEST_EXECUTOR.value.output_validation_fn
            )
            if not validation_method:
                self.logger.warning(
                    "No output validation method defined for PortfolioBacktestExecutor."
                )
                return False
            return validation_method(output_data, self.logger)
        except Exception as e:
            self.logger.error(
                f"Error validating output data for PortfolioBacktestExecutor: {e}"
            )
            return False
