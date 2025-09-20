from enum import Enum


class LoggerEnv(Enum):
    # TRADING = "trading"
    # BACKTEST = "backtest"

    PROD = "prod"
    TEST = "test"
    UNIT = "unit"
    INTEGRATION = "integration"
