from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Task:
    id: str
    name: str
    interval_days: int
    strict: bool
    last_done: datetime | None = None

    def next_due(self, now: datetime) -> datetime:
        if self.last_done is None:
            return now  # immediately due

        if self.strict:
            return self.last_done + timedelta(days=self.interval_days)

        # non-strict → same behavior for now (will improve later)
        return self.last_done + timedelta(days=self.interval_days)

    def is_due(self, now: datetime) -> bool:
        return now >= self.next_due(now)

    def days_until(self, now: datetime) -> int:
        delta = self.next_due(now) - now
        return int(delta.total_seconds() // 86400)
