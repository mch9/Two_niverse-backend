from sqlalchemy import Column, Integer, String, Date, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.persistence.database import Base


class FestivalModel(Base):
    __tablename__ = "festivals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kopis_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    venue = Column(String(200))
    area = Column(String(100))
    genre = Column(String(50))
    age_limit = Column(String(100))
    price_info = Column(Text)
    poster_url = Column(String(500))
    local_poster = Column(String(300))
    schedule = Column(Text)
    cast_info = Column(Text)
    producer = Column(String(500))
    is_festival = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    ticket_links = relationship("TicketLinkModel", back_populates="festival", cascade="all, delete-orphan")


class TicketLinkModel(Base):
    __tablename__ = "ticket_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    festival_id = Column(Integer, ForeignKey("festivals.id", ondelete="CASCADE"), nullable=False)
    vendor_name = Column(String(100))
    url = Column(String(500))

    festival = relationship("FestivalModel", back_populates="ticket_links")


class BlogPostModel(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    festival_kopis_id = Column(String(20), ForeignKey("festivals.kopis_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    link = Column(String(500), nullable=False)
    blogger_name = Column(String(100))
    post_date = Column(String(20))
    fetched_at = Column(DateTime, server_default=func.now())
