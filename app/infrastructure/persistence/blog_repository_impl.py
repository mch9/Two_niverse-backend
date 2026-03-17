from sqlalchemy.orm import Session
from app.domain.blog.entity import BlogPost
from app.domain.blog.repository import BlogPostRepository
from app.infrastructure.persistence.models import BlogPostModel


class SqlAlchemyBlogPostRepository(BlogPostRepository):
    def __init__(self, session: Session):
        self.session = session

    def save_all(self, posts: list[BlogPost]) -> None:
        for post in posts:
            model = BlogPostModel(
                festival_kopis_id=post.festival_kopis_id,
                title=post.title,
                link=post.link,
                blogger_name=post.blogger_name,
                post_date=post.post_date,
            )
            self.session.add(model)
        self.session.commit()

    def find_by_festival_id(self, festival_kopis_id: str) -> list[BlogPost]:
        models = self.session.query(BlogPostModel).filter_by(
            festival_kopis_id=festival_kopis_id
        ).all()
        return [
            BlogPost(
                title=m.title,
                link=m.link,
                blogger_name=m.blogger_name,
                post_date=m.post_date,
                festival_kopis_id=m.festival_kopis_id,
            )
            for m in models
        ]

    def delete_by_festival_id(self, festival_kopis_id: str) -> None:
        self.session.query(BlogPostModel).filter_by(
            festival_kopis_id=festival_kopis_id
        ).delete()
        self.session.commit()
