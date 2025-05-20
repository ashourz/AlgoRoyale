import asyncio

class PipelineCoordinator:
    def __init__(self, data_loader, backtest_executor, data_preparer, logger, config_validator, strategy_factory):
        self.logger = logger
        self.config_validator = config_validator
        self.strategy_factory = strategy_factory
        self.data_loader = data_loader
        self.data_preparer = data_preparer
        self.backtest_executor = backtest_executor

    async def run_async(self, config=None):
        try:
            # 1. Validate and normalize configuration
            config = self.config_validator.validate(config or {})
            if not config:
                self.logger.error("Invalid configuration")
                return False
            # 2. Initialize strategies
            strategies = self.strategy_factory.create_strategies(config)
            if not strategies:
                self.logger.error("No strategies initialized")
                return False
            # 3. Load data
            raw_data = await self.data_loader.load_all()
            if not raw_data:
                self.logger.error("No data loaded")
                return False
            # 4. Prepare data
            prepared_data = {}
            for symbol, df_iter_factory in raw_data.items():
                async def prepared_iter():
                    async for df in df_iter_factory():
                        try:
                            yield self.data_preparer.normalize_dataframe(df, config, symbol)
                        except Exception as e:
                            self.logger.error(f"Error preparing {symbol}: {e}")
                            continue
                prepared_data[symbol] = prepared_iter
            if not prepared_data:
                self.logger.error("No valid data available for backtesting")
                return False
            # 5. Run backtest
            self.logger.info("Starting backtest...")
            await self.backtest_executor.run_backtest(strategies, prepared_data)
            self.logger.info("Backtest completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return False

    def run(self, config=None):
        return asyncio.run(self.run_async(config=config))