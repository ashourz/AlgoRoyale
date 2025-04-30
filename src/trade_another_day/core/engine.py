


class BacktestEngine:
    def __init__(self, strategy: BaseStrategy):
        self.strategy = strategy
        self.symbols = get_watchlist()

    def run(self):
        for symbol in self.symbols:
            print(f"[•] Running backtest for {symbol}...")

            # Step 1: Load data
            df = load_symbol_data(symbol)
            if df.empty:
                print(f"[!] No data for {symbol}, skipping.")
                continue

            # Step 2: Run strategy
            results = self.strategy.run(df)

            # Step 3: Save results
            save_results(self.strategy.name, symbol, results)

        print("[✓] Backtest completed for all symbols.")
