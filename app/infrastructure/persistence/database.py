from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Database:
    _engine = None
    _session_factory = None

    @classmethod
    def init(cls, database_uri: str):
        cls._engine = create_engine(database_uri, echo=False)
        cls._session_factory = sessionmaker(bind=cls._engine)
        Base.metadata.create_all(bind=cls._engine)

    @classmethod
    def get_session(cls):
        return cls._session_factory()
