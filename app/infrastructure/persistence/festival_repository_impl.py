from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from app.domain.festival.entity import Festival
from app.domain.festival.value_objects import Period, TicketLink
from app.domain.festival.repository import FestivalRepository
from app.infrastructure.persistence.models import FestivalModel, TicketLinkModel


class SqlAlchemyFestivalRepository(FestivalRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, festival: Festival) -> None:
        existing = self.session.query(FestivalModel).filter_by(
            kopis_id=festival.kopis_id
        ).first()

        if existing:
            existing.name = festival.name
            existing.start_date = festival.period.start_date
            existing.end_date = festival.period.end_date
            existing.venue = festival.venue
            existing.area = festival.area
            existing.genre = festival.genre
            existing.age_limit = festival.age_limit
            existing.price_info = festival.price_info
            existing.poster_url = festival.poster_url
            existing.local_poster = festival.local_poster_path
            existing.schedule = festival.schedule
            existing.cast_info = festival.cast_info
            existing.producer = festival.producer
            existing.is_festival = festival.is_festival
            # ticket links 갱신
            existing.ticket_links.clear()
            for tl in festival.ticket_links:
                existing.ticket_links.append(
                    TicketLinkModel(vendor_name=tl.vendor_name, url=tl.url)
                )
        else:
            model = FestivalModel(
                kopis_id=festival.kopis_id,
                name=festival.name,
                start_date=festival.period.start_date,
                end_date=festival.period.end_date,
                venue=festival.venue,
                area=festival.area,
                genre=festival.genre,
                age_limit=festival.age_limit,
                price_info=festival.price_info,
                poster_url=festival.poster_url,
                local_poster=festival.local_poster_path,
                schedule=festival.schedule,
                cast_info=festival.cast_info,
                producer=festival.producer,
                is_festival=festival.is_festival,
                ticket_links=[
                    TicketLinkModel(vendor_name=tl.vendor_name, url=tl.url)
                    for tl in festival.ticket_links
                ],
            )
            self.session.add(model)

        self.session.commit()

    def find_by_kopis_id(self, kopis_id: str) -> Festival | None:
        model = self.session.query(FestivalModel).filter_by(
            kopis_id=kopis_id
        ).first()
        if not model:
            return None
        return self._to_entity(model)

    def find_all(self) -> list[Festival]:
        models = self.session.query(FestivalModel).order_by(
            FestivalModel.start_date
        ).all()
        return [self._to_entity(m) for m in models]

    def search(
        self,
        keyword: str | None = None,
        area: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        festival_only: bool = False,
    ) -> list[Festival]:
        query = self.session.query(FestivalModel)

        if keyword:
            query = query.filter(FestivalModel.name.like(f"%{keyword}%"))
        if area:
            query = query.filter(FestivalModel.area == area)
        if start_date:
            query = query.filter(FestivalModel.end_date >= start_date)
        if end_date:
            query = query.filter(FestivalModel.start_date <= end_date)
        if festival_only:
            query = query.filter(FestivalModel.is_festival == True)

        models = query.order_by(FestivalModel.start_date).all()
        return [self._to_entity(m) for m in models]

    def get_all_areas(self) -> list[str]:
        results = self.session.query(distinct(FestivalModel.area)).order_by(
            FestivalModel.area
        ).all()
        return [r[0] for r in results if r[0]]

    def _to_entity(self, model: FestivalModel) -> Festival:
        return Festival(
            kopis_id=model.kopis_id,
            name=model.name,
            period=Period(
                start_date=model.start_date,
                end_date=model.end_date,
            ),
            venue=model.venue,
            area=model.area,
            genre=model.genre,
            age_limit=model.age_limit,
            price_info=model.price_info,
            poster_url=model.poster_url,
            local_poster_path=model.local_poster,
            schedule=model.schedule,
            cast_info=model.cast_info,
            producer=model.producer,
            is_festival=model.is_festival,
            ticket_links=[
                TicketLink(vendor_name=tl.vendor_name, url=tl.url)
                for tl in model.ticket_links
            ],
        )
