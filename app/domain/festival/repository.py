from abc import ABC, abstractmethod
from datetime import date
from app.domain.festival.entity import Festival


class FestivalRepository(ABC):
    @abstractmethod
    def save(self, festival: Festival) -> None:
        pass

    @abstractmethod
    def find_by_kopis_id(self, kopis_id: str) -> Festival | None:
        pass

    @abstractmethod
    def find_all(self) -> list[Festival]:
        pass

    @abstractmethod
    def search(
        self,
        keyword: str | None = None,
        area: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        festival_only: bool = False,
    ) -> list[Festival]:
        pass

    @abstractmethod
    def get_all_areas(self) -> list[str]:
        pass
