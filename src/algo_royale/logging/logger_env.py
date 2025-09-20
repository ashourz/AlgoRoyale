from enum import Enum


class ApplicationEnv(Enum):
    # TRADING = "trading"
    # BACKTEST = "backtest"

    PROD = "prod"
    TEST = "test"
    UNIT = "unit"
    INTEGRATION = "integration"
