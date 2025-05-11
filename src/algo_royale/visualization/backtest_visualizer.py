from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


class BacktestVisualizer:
    """
    BacktestVisualizer is a class for visualizing backtesting results.
    It provides methods to plot equity curves, drawdowns, trades, and performance metrics.
    It can also generate heatmaps for performance metrics.
    """

    def __init__(self, data=None, file_path=None):
        """
        Initialize the visualizer with either a DataFrame or file path to CSV

        Args:
            data (pd.DataFrame, optional): Backtesting results DataFrame
            file_path (str, optional): Path to CSV file with backtesting results
        """
        if data is not None:
            self.data = data.copy()
        elif file_path is not None:
            self.data = pd.read_csv(file_path, parse_dates=["timestamp"])
        else:
            raise ValueError("Either data or file_path must be provided")

        # Ensure timestamp is datetime and set as index
        if not pd.api.types.is_datetime64_any_dtype(self.data["timestamp"]):
            self.data["timestamp"] = pd.to_datetime(self.data["timestamp"])
        self.data.set_index("timestamp", inplace=True)

        # Preprocess data
        self._preprocess_data()

    def _preprocess_data(self):
        """Preprocess data for analysis"""
        # Calculate returns
        self.data["returns"] = self.data["close"].pct_change()

        # Calculate strategy returns (assuming signal is for next period)
        self.data["strategy_returns"] = (
            self.data["signal"].shift(1).eq("buy").astype(int) * self.data["returns"]
        )

        # Calculate cumulative returns
        self.data["cumulative_market"] = (1 + self.data["returns"]).cumprod()
        self.data["cumulative_strategy"] = (1 + self.data["strategy_returns"]).cumprod()

        # Calculate drawdowns
        self.data["peak_market"] = self.data["cumulative_market"].cummax()
        self.data["drawdown_market"] = (
            self.data["cumulative_market"] - self.data["peak_market"]
        ) / self.data["peak_market"]

        self.data["peak_strategy"] = self.data["cumulative_strategy"].cummax()
        self.data["drawdown_strategy"] = (
            self.data["cumulative_strategy"] - self.data["peak_strategy"]
        ) / self.data["peak_strategy"]

    def plot_equity_curve(self, strategies=None, symbols=None, title="Equity Curve"):
        """
        Plot cumulative returns for strategies/symbols

        Args:
            strategies (list, optional): List of strategies to include. If None, all strategies.
            symbols (list, optional): List of symbols to include. If None, all symbols.
            title (str): Title for the plot

        Returns:
            plotly.graph_objects.Figure
        """
        # Filter data if needed
        df = self.data.copy()
        if strategies is not None:
            df = df[df["strategy"].isin(strategies)]
        if symbols is not None:
            df = df[df["symbol"].isin(symbols)]

        # Group by strategy and symbol
        grouped = df.groupby(["strategy", "symbol"])

        fig = go.Figure()

        for (strategy, symbol), group in grouped:
            fig.add_trace(
                go.Scatter(
                    x=group.index,
                    y=group["cumulative_strategy"],
                    mode="lines",
                    name=f"{symbol} - {strategy}",
                    hovertemplate="<b>%{fullData.name}</b><br>"
                    + "Date: %{x|%Y-%m-%d %H:%M}<br>"
                    + "Value: %{y:.2f}<br>"
                    + "<extra></extra>",
                )
            )

        # Add market performance if only one symbol is selected
        if symbols is not None and len(symbols) == 1:
            market_data = df[df["symbol"] == symbols[0]]
            fig.add_trace(
                go.Scatter(
                    x=market_data.index,
                    y=market_data["cumulative_market"],
                    mode="lines",
                    name=f"{symbols[0]} - Market",
                    line=dict(dash="dot"),
                    hovertemplate="<b>Market</b><br>"
                    + "Date: %{x|%Y-%m-%d %H:%M}<br>"
                    + "Value: %{y:.2f}<br>"
                    + "<extra></extra>",
                )
            )

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Cumulative Returns",
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            template="plotly_white",
        )

        return fig

    def plot_drawdown(self, strategies=None, symbols=None, title="Drawdown"):
        """
        Plot drawdown for strategies/symbols

        Args:
            strategies (list, optional): List of strategies to include
            symbols (list, optional): List of symbols to include
            title (str): Title for the plot

        Returns:
            plotly.graph_objects.Figure
        """
        # Filter data if needed
        df = self.data.copy()
        if strategies is not None:
            df = df[df["strategy"].isin(strategies)]
        if symbols is not None:
            df = df[df["symbol"].isin(symbols)]

        # Group by strategy and symbol
        grouped = df.groupby(["strategy", "symbol"])

        fig = go.Figure()

        for (strategy, symbol), group in grouped:
            fig.add_trace(
                go.Scatter(
                    x=group.index,
                    y=group["drawdown_strategy"] * 100,  # as percentage
                    mode="lines",
                    name=f"{symbol} - {strategy}",
                    hovertemplate="<b>%{fullData.name}</b><br>"
                    + "Date: %{x|%Y-%m-%d %H:%M}<br>"
                    + "Drawdown: %{y:.2f}%<br>"
                    + "<extra></extra>",
                )
            )

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            template="plotly_white",
        )

        return fig

    def plot_trades(self, symbol, strategy, days=1, title="Trade Signals"):
        """
        Plot price and trade signals for a specific symbol and strategy

        Args:
            symbol (str): Symbol to plot
            strategy (str): Strategy to plot
            days (int): Number of days to show (from end of data)
            title (str): Title for the plot

        Returns:
            plotly.graph_objects.Figure
        """
        # Filter data
        df = self.data[
            (self.data["symbol"] == symbol) & (self.data["strategy"] == strategy)
        ].copy()

        # Get last N days
        if days is not None:
            start_date = df.index.max() - pd.Timedelta(days=days)
            df = df[df.index >= start_date]

        # Create figure with subplots
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
        )

        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name=f"{symbol} OHLC",
            ),
            row=1,
            col=1,
        )

        # Add buy/sell signals
        buys = df[df["signal"] == "buy"]
        sells = df[df["signal"] == "sell"]

        fig.add_trace(
            go.Scatter(
                x=buys.index,
                y=buys["low"] * 0.99,
                mode="markers",
                marker=dict(color="green", size=10, symbol="triangle-up"),
                name="Buy Signal",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=sells.index,
                y=sells["high"] * 1.01,
                mode="markers",
                marker=dict(color="red", size=10, symbol="triangle-down"),
                name="Sell Signal",
            ),
            row=1,
            col=1,
        )

        # Volume
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["volume"],
                name="Volume",
                marker_color="rgba(100, 100, 100, 0.5)",
            ),
            row=2,
            col=1,
        )

        # Update layout
        fig.update_layout(
            title=f"{title} - {symbol} - {strategy}",
            height=600,
            hovermode="x unified",
            showlegend=True,
            template="plotly_white",
            xaxis_rangeslider_visible=False,
        )

        return fig

    def performance_metrics(self, strategies=None, symbols=None, risk_free_rate=0.0):
        """
        Calculate performance metrics for strategies

        Args:
            strategies (list, optional): List of strategies to include
            symbols (list, optional): List of symbols to include
            risk_free_rate (float): Risk-free rate for Sharpe ratio calculation

        Returns:
            pd.DataFrame: DataFrame with performance metrics
        """
        # Filter data if needed
        df = self.data.copy()
        if strategies is not None:
            df = df[df["strategy"].isin(strategies)]
        if symbols is not None:
            df = df[df["symbol"].isin(symbols)]

        # Group by strategy and symbol
        grouped = df.groupby(["strategy", "symbol"])

        metrics = []

        for (strategy, symbol), group in grouped:
            if len(group) < 2:
                continue

            # Calculate metrics
            total_return = group["cumulative_strategy"].iloc[-1] - 1
            annualized_return = (1 + total_return) ** (
                252 / (len(group) / (6.5 * 60))
            ) - 1  # Assuming minute data, 6.5 trading hours/day

            returns = group["strategy_returns"].dropna()
            volatility = returns.std() * np.sqrt(
                252 * 6.5 * 60
            )  # Annualized volatility for minute data
            sharpe_ratio = (
                (returns.mean() * 252 * 6.5 * 60 - risk_free_rate) / (volatility)
                if volatility > 0
                else 0
            )

            max_drawdown = group["drawdown_strategy"].min()

            # Count trades
            trades = group["signal"].value_counts()
            buy_trades = trades.get("buy", 0)
            sell_trades = trades.get("sell", 0)

            metrics.append(
                {
                    "Strategy": strategy,
                    "Symbol": symbol,
                    "Total Return (%)": total_return * 100,
                    "Annualized Return (%)": annualized_return * 100,
                    "Annualized Volatility (%)": volatility * 100,
                    "Sharpe Ratio": sharpe_ratio,
                    "Max Drawdown (%)": max_drawdown * 100,
                    "Buy Trades": buy_trades,
                    "Sell Trades": sell_trades,
                    "Total Trades": buy_trades + sell_trades,
                }
            )

        return pd.DataFrame(metrics)

    def plot_metrics_heatmap(
        self,
        metric="Total Return (%)",
        strategies=None,
        symbols=None,
        title="Performance Heatmap",
    ):
        """
        Plot performance metrics as a heatmap

        Args:
            metric (str): Metric to plot
            strategies (list, optional): List of strategies to include
            symbols (list, optional): List of symbols to include
            title (str): Title for the plot

        Returns:
            plotly.graph_objects.Figure
        """
        metrics_df = self.performance_metrics(strategies=strategies, symbols=symbols)

        if metrics_df.empty:
            raise ValueError("No data available for the selected strategies/symbols")

        # Pivot for heatmap
        heatmap_data = metrics_df.pivot(
            index="Strategy", columns="Symbol", values=metric
        )

        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Symbol", y="Strategy", color=metric),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdYlGn",
        )

        fig.update_layout(
            title=title,
            xaxis_title="Symbol",
            yaxis_title="Strategy",
            template="plotly_white",
        )

        return fig
