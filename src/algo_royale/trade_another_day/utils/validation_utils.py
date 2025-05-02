
from datetime import datetime

from algo_royale.trade_another_day.exceptions import InvalidDateFormatError
import dateutil


def validate_date(date_str: str, field_name: str) -> None:
    """Validate RFC3339 format or raise ValueError."""
    try:
        parsed = dateutil.parser.parse(date_str)
        if not parsed.tzinfo:
            raise ValueError(f"Missing timezone in {field_name}. RFC3339 requires timezone (e.g., 'Z' or '+00:00').")
    except ValueError as e:
        raise InvalidDateFormatError(
            f"Invalid {field_name}: '{date_str}'. Expected RFC3339 format (e.g., '2022-01-01T00:00:00Z')."
        ) from e