"""Manages the collection of available strategies and resolves them per symbol.
State of symbol-strategy pairs is maintained in the strategy registry.
Daily or on-demand update reports are generated to track changes in strategy availability and use.
"""

import json


class StrategyRegistry:
    def __init__(self, config_path):
        self.config_path = config_path
        self.state = {}

    def load_state(self):
        with open(self.config_path) as f:
            self.state = json.load(f)

    def get_strategies(self, symbol):
        return self.state.get(symbol, [])

    def write_report(self, filename, timestamp):
        report = {"timestamp": timestamp.isoformat(), "strategies": self.state}
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)


# Usage example:
# registry = StrategyRegistry("strategies.json")
# registry.load_state()
# registry.write_report("start_of_day_report.json", datetime.now())
