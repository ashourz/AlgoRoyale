import pandas as pd

class Portfolio:
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = []
        self.history = []

    def run(self, data: pd.DataFrame, signals: pd.Series):
        for date, signal in signals.items():
            price = data.loc[date, 'Close']
            if signal == 1:  # Buy
                self.positions.append(price)
                self.cash -= price
            elif signal == -1 and self.positions:  # Sell
                entry_price = self.positions.pop()
                self.cash += price
            self.history.append(self.portfolio_value(price))

    def portfolio_value(self, current_price: float) -> float:
        return self.cash + sum(current_price for _ in self.positions)