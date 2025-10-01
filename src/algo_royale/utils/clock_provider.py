from datetime import datetime, timezone


class ClockProvider:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
