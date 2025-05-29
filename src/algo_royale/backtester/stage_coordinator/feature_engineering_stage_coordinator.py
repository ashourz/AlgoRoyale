from logging import Logger
from typing import AsyncIterator, Callable, Dict

import pandas as pd

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.feature_engineering.feature_engineer import (
    FeatureEngineer,
)
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter


class FeatureEngineeringStageCoordinator(StageCoordinator):
    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        feature_engineer: FeatureEngineer,
    ):
        super().__init__(
            stage=BacktestStage.FEATURE_ENGINEERING,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.feature_engineer = feature_engineer

    async def process(
        self, prepared_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """
        Process the prepared data for this stage.
        Should return a dict: symbol -> async generator or DataFrame.
        """
        engineered_data = await self._engineer(prepared_data)
        if not engineered_data:
            self.logger.error("Feature engineering failed")
            return {}
        return engineered_data

    async def _engineer(
        self, ingest_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        engineered = {}
        for symbol, df_iter_factory in ingest_data.items():
            engineered[symbol] = (
                lambda symbol=symbol,
                df_iter_factory=df_iter_factory: self.feature_engineer.engineer_features(
                    df_iter_factory(), symbol
                )
            )
        return engineered
