import os
from flask import Flask
from app.config import Config
from app.infrastructure.persistence.database import Database
from app.infrastructure.persistence.festival_repository_impl import SqlAlchemyFestivalRepository
from app.infrastructure.persistence.blog_repository_impl import SqlAlchemyBlogPostRepository
from app.infrastructure.external_api.kopis_client import KopisClient
from app.infrastructure.external_api.naver_blog_client import NaverBlogClient
from app.application.festival_service import FestivalApplicationService
from app.application.blog_service import BlogApplicationService


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
