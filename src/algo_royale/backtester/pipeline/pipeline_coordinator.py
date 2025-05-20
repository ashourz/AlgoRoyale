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
            self.logger.info("Validating configuration...")
            config = self._validate_config(config)
            if not config:
                self.logger.error("Invalid configuration")
                return False
            # 2. Initialize strategies
            self.logger.info("Initializing strategies...")
            strategies = self._initialize_strategies(config)
            if not strategies:
                self.logger.error("No strategies initialized")
                return False
            # 3. Load data
            self.logger.info("Loading data...")
            raw_data = await self._load_data()
            if not raw_data:
                self.logger.error("No data loaded")
                return False
            # 4. Prepare data
            self.logger.info("Preparing data...")
            prepared_data = self._prepare_data(config, raw_data)
            if not prepared_data:
                self.logger.error("No valid data available for backtesting")
                return False
            # 5. Run backtest
            self.logger.info("Starting backtest...")
            backtest_result = await self._run_backtest(strategies, prepared_data)
            if not backtest_result:
                self.logger.error("Backtest failed")
                return False
            await self.backtest_executor.save_results()
            self.logger.info("Backtest Pipeline completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return False

    def run(self, config=None):
        return asyncio.run(self.run_async(config=config))
    
    def _validate_config(self, config: dict) -> dict:
        """Validate and normalize configuration"""
        try:
            config = self.config_validator.validate(config or {})
            return config
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def _initialize_strategies(self, config: dict) -> list:
        """Initialize strategies based on the configuration"""
        try:
            strategies = self.strategy_factory.create_strategies(config)            
            return strategies
        except Exception as e:
            self.logger.error(f"Strategy initialization failed: {e}")
            return False
        
    async def _load_data(self) -> dict:
        """Load data based on the configuration"""
        try:
            data = await self.data_loader.load_all()            
            return data
        except Exception as e:
            self.logger.error(f"Data loading failed: {e}")
            return False
        
    def _prepare_data(self, config: dict, data: dict) -> dict:
        """Prepare data for backtesting"""
        try:
            prepared_data = {}
            for symbol, df_iter_factory in data.items():
                prepared_data[symbol] = lambda symbol=symbol, df_iter_factory=df_iter_factory: self.data_preparer.normalized_stream(symbol, df_iter_factory, config)
            return prepared_data    
        except Exception as e:
            self.logger.error(f"Data preparation failed: {e}")
            return False
        
    async def _run_backtest(self, strategies: list, prepared_data: dict) -> bool:
        """Run backtest using the prepared data and strategies"""
        try:
            await self.backtest_executor.run_backtest(strategies, prepared_data)
            return True
        except Exception as e:
            self.logger.error(f"Backtest execution failed: {e}")
            return False