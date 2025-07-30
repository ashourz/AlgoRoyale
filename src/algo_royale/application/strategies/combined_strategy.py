from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)


class CombinedStrategy:
    def __init__(self, strategy_viability: dict[BaseSignalStrategy, float]):
        assert isinstance(strategy_viability, dict)
        self.strategy_viability = strategy_viability

    def generate_signal(self, data):
        signals = [s.generate_signals(data) for s in self.strategy_viability.keys()]
        viability = list(self.strategy_viability.values())
        total_viability = sum(viability)
        weights = (
            [v / total_viability for v in viability]
            if total_viability
            else [0] * len(viability)
        )
        if total_viability == 0:
            return 0  # or handle as appropriate
        weighted_signal = sum(w * s for w, s in zip(weights, signals)) / total_viability
        return weighted_signal

    def get_strategy_signal(self, data, strategy: BaseSignalStrategy):
        """
        Generate a combined signal based on the individual strategy signals and their viability.
        """
        signals_df = strategy.generate_signals(data)
