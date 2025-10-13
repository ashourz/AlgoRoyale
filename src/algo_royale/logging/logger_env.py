from enum import Enum

from algo_royale.utils.path_utils import get_config_dir, get_secrets_dir


class ApplicationEnv(Enum):
    PROD_LIVE = "prod_live"
    PROD_PAPER = "prod_paper"
    DEV_INTEGRATION = "dev_integration"
    DEV_UNIT = "dev_unit"

    @property
    def config_ini_path(self) -> str:
        base = get_config_dir()
        if self is ApplicationEnv.PROD_LIVE:
            return str(base / "env_config_prod_live.ini")
        elif self is ApplicationEnv.PROD_PAPER:
            return str(base / "env_config_prod_paper.ini")
        elif self is ApplicationEnv.DEV_INTEGRATION:
            return str(base / "env_config_dev_integration.ini")
        else:
            raise ValueError(f"Unsupported environment: {self}")

    @property
    def secrets_ini_path(self) -> str:
        base = get_secrets_dir()
        if self is ApplicationEnv.PROD_LIVE:
            return str(base / "env_secrets_prod_live.ini")
        elif self is ApplicationEnv.PROD_PAPER:
            return str(base / "env_secrets_prod_paper.ini")
        elif self is ApplicationEnv.DEV_INTEGRATION:
            return str(base / "env_secrets_dev_integration.ini")
        else:
            raise ValueError(f"Unsupported environment: {self}")
