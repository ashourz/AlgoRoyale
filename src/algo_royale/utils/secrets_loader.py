import os
from configparser import ConfigParser
from typing import Optional

from algo_royale.utils.path_utils import get_secrets_dir


def load_env_secrets(env_name: str, secrets_dir: Optional[str] = None) -> None:
    """
    Load secrets from secrets/env_secrets_{env_name}.ini and export them to os.environ.

    Exports both generic SECTION_KEY names (e.g., PORTALOCKER_CONTROL_TOKEN) and a
    prefixed ALGO_ROYALE_SECTION_KEY name. Additionally maps portalocker CONTROL_TOKEN
    -> ALGO_ROYALE_CONTROL_TOKEN for compatibility with the control server.
    """
    base = secrets_dir or os.path.join(os.getcwd(), "secrets")
    path = os.path.join(base, f"env_secrets_{env_name}.ini")
    if not os.path.exists(path):
        # no-op if secrets file missing
        return

    cfg = ConfigParser()
    cfg.read(path)

    for section in cfg.sections():
        for key, value in cfg.items(section):
            # Normalize to uppercase and replace non-alphanum with _
            sec = section.upper()
            k = key.upper()
            env_key = f"{sec}_{k}"
            alt_key = f"ALGO_ROYALE_{sec}_{k}"
            os.environ[env_key] = value
            os.environ[alt_key] = value

            # Special mapping: portalocker CONTROL_TOKEN -> ALGO_ROYALE_CONTROL_TOKEN
            if sec == "PORTALOCKER" and k in ("CONTROL_TOKEN", "CONTROLTOKEN"):
                os.environ["ALGO_ROYALE_CONTROL_TOKEN"] = value


def get_control_token(env_name: str) -> Optional[str]:
    """Read the portalocker control token value from the env_secrets file without exporting it.

    Returns the token string or None if not found.
    """
    base = get_secrets_dir()
    path = os.path.join(base, f"env_secrets_{env_name}.ini")
    if not os.path.exists(path):
        return None
    cfg = ConfigParser()
    cfg.read(path)
    if cfg.has_section("portalocker"):
        # try common keys
        for key in ("control_token", "controltoken", "token"):
            if cfg.has_option("portalocker", key):
                return cfg.get("portalocker", key)
    return None
