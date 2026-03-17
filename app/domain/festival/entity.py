from datetime import date
from app.domain.festival.value_objects import Period, TicketLink


class Festival:
    def __init__(
        self,
        kopis_id: str,
        name: str,
        period: Period,
        venue: str,
        area: str,
        genre: str,
        age_limit: str | None = None,
        price_info: str | None = None,
        poster_url: str | None = None,
        local_poster_path: str | None = None,
        schedule: str | None = None,
        cast_info: str | None = None,
        producer: str | None = None,
        is_festival: bool = False,
        ticket_links: list[TicketLink] | None = None,
    ):
        self.kopis_id = kopis_id
        self.name = name
        self.period = period
        self.venue = venue
        self.area = area
        self.genre = genre
        self.age_limit = age_limit
        self.price_info = price_info
        self.poster_url = poster_url
        self.local_poster_path = local_poster_path
        self.schedule = schedule
        self.cast_info = cast_info
        self.producer = producer
        self.is_festival = is_festival
        self.ticket_links = ticket_links or []

    @property
    def is_ongoing(self) -> bool:
        today = date.today()
        return self.period.start_date <= today <= self.period.end_date

    @property
    def search_keyword(self) -> str:
        return self.name
