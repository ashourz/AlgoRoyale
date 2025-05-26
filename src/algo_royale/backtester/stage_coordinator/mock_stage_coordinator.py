from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator


class MockStageCoordinator(StageCoordinator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_called = False
        self.process_return = {}

    async def process(self, prepared_data):
        self.process_called = True
        return self.process_return
