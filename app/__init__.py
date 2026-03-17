import os
import threading
from datetime import datetime, date
from flask import Flask
from app.config import Config
from app.infrastructure.persistence.database import Database
from app.infrastructure.persistence.festival_repository_impl import SqlAlchemyFestivalRepository
from app.infrastructure.persistence.blog_repository_impl import SqlAlchemyBlogPostRepository
from app.infrastructure.external_api.kopis_client import KopisClient
from app.infrastructure.external_api.naver_blog_client import NaverBlogClient
from app.application.festival_service import FestivalApplicationService
from app.application.blog_service import BlogApplicationService


def _collect_festivals(kopis_client, poster_dir):
    """DB가 비어있으면 초기 데이터 수집"""
    session = Database.get_session()
    try:
        repo = SqlAlchemyFestivalRepository(session)
        if repo.count() > 0:
            return

        service = FestivalApplicationService(
            festival_repo=repo,
            kopis_client=kopis_client,
            poster_dir=poster_dir,
        )

        today = date.today()
        stdate = today.strftime("%Y%m01")
        eddate = today.strftime("%Y%m%d")

        service.collect_festivals("축제", stdate, eddate)
        service.collect_festivals("페스티벌", stdate, eddate)
    finally:
        session.close()


def _scheduled_collect(kopis_client, poster_dir):
    """매일 실행되는 정기 수집"""
    session = Database.get_session()
    try:
        repo = SqlAlchemyFestivalRepository(session)
        service = FestivalApplicationService(
            festival_repo=repo,
            kopis_client=kopis_client,
            poster_dir=poster_dir,
        )

        today = date.today()
        stdate = today.strftime("%Y%m01")
        eddate = today.strftime("%Y%m%d")

        service.collect_festivals("축제", stdate, eddate)
        service.collect_festivals("페스티벌", stdate, eddate)
    finally:
        session.close()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "presentation", "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )
    app.secret_key = os.getenv("SECRET_KEY", "dev-only-change-in-prod")

    # DB 초기화
    Database.init(Config.SQLALCHEMY_DATABASE_URI)

    # API 클라이언트
    kopis_client = KopisClient(api_key=Config.KOPIS_API_KEY)
    naver_client = NaverBlogClient(
        client_id=Config.NAVER_CLIENT_ID,
        client_secret=Config.NAVER_CLIENT_SECRET,
    )

    # 앱 시작 시 초기 데이터 수집 (백그라운드)
    threading.Thread(
        target=_collect_festivals,
        args=(kopis_client, Config.POSTER_DIR),
        daemon=True,
    ).start()

    # 매일 새벽 3시 자동 수집 스케줄러
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _scheduled_collect,
        "cron",
        hour=3,
        args=[kopis_client, Config.POSTER_DIR],
    )
    scheduler.start()

    # 요청마다 세션을 생성하는 서비스 팩토리
    @app.before_request
    def setup_services():
        from flask import g
        g.db_session = Database.get_session()

        festival_repo = SqlAlchemyFestivalRepository(g.db_session)
        blog_repo = SqlAlchemyBlogPostRepository(g.db_session)

        app.config["FESTIVAL_SERVICE"] = FestivalApplicationService(
            festival_repo=festival_repo,
            kopis_client=kopis_client,
            poster_dir=Config.POSTER_DIR,
        )
        app.config["BLOG_SERVICE"] = BlogApplicationService(
            blog_repo=blog_repo,
            naver_client=naver_client,
        )

    @app.teardown_request
    def teardown_session(exception=None):
        from flask import g
        session = g.pop("db_session", None)
        if session:
            session.close()

    # 라우트 등록
    from app.presentation.routes import bp
    app.register_blueprint(bp)

    return app
