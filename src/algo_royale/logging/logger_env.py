from enum import Enum


class ApplicationEnv(Enum):
    # TRADING = "trading"
    # BACKTEST = "backtest"

    # PROD = "prod"
    # TEST = "test"
    # UNIT = "unit"
    # INTEGRATION = "integration"
    PROD_LIVE = "prod_live"
    PROD_PAPER = "prod_paper"
    DEV_INTEGRATION = "dev_integration"
    DEV_UNIT = "dev_unit"
