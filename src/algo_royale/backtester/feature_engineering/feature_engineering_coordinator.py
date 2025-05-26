from logging import Logger

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.feature_engineering.feature_engineer import (
    FeatureEngineer,
)
from algo_royale.backtester.pipeline.data_manage.stage_data_loader import (
    StageDataLoader,
)
from algo_royale.backtester.pipeline.data_manage.stage_data_writer import (
    StageDataWriter,
)


class FeatureEngineeringCoordinator:
    def __init__(
        self,
        data_loader: StageDataLoader,
        feature_engineer: FeatureEngineer,
        data_writer: StageDataWriter,
        logger: Logger,
    ):
        self.data_loader = data_loader
        self.feature_engineer = feature_engineer
        self.data_writer = data_writer
        self.logger = logger

    async def run(self, config: dict) -> bool:
        """
        Run the feature engineering process:
        1. Load data from the ingest stage.
        2. Engineer features using the FeatureEngineer class.
        3. Write the engineered data to the feature engineering stage.
        """
        ingest_data = await self._load_data(config)
        if not ingest_data:
            self.logger.error("No ingest data loaded")
            return False

        engineered_data = await self._engineer(ingest_data, config)
        if not engineered_data:
            self.logger.error("Feature engineering failed")
            return False

        await self._write(engineered_data)
        self.logger.info("Feature engineering completed and files saved.")
        return True

    async def _load_data(self, config):
        return await self.data_loader.load_all_stage_data(
            stage=BacktestStage.DATA_INGEST
        )

    async def _engineer(self, ingest_data, config):
        engineered = {}
        for symbol, df_iter_factory in ingest_data.items():
            engineered[symbol] = (
                lambda symbol=symbol,
                df_iter_factory=df_iter_factory: self.feature_engineer.engineer_features(
                    df_iter_factory(), config, symbol
                )
            )
        return engineered

    async def _write(self, engineered_data):
        for symbol, df_iter_factory in engineered_data.items():
            async for df in df_iter_factory():
                self.data_writer.save_stage_data(
                    stage=BacktestStage.FEATURE_ENGINEERING,
                    symbol=symbol,
                    results_df=df,
                )
