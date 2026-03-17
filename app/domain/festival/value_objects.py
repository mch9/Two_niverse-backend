from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Period:
    start_date: date
    end_date: date

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1


@dataclass(frozen=True)
class TicketLink:
    vendor_name: str
    url: str
