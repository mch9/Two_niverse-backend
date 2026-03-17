from app.domain.blog.entity import BlogPost
from app.domain.blog.repository import BlogPostRepository
from app.domain.festival.entity import Festival
from app.infrastructure.external_api.naver_blog_client import NaverBlogClient


class BlogApplicationService:
    def __init__(
        self,
        blog_repo: BlogPostRepository,
        naver_client: NaverBlogClient,
    ):
        self.blog_repo = blog_repo
        self.naver_client = naver_client

    def fetch_blogs_for_festival(self, festival: Festival) -> list[BlogPost]:
        """페스티벌 관련 블로그 검색. 이미 저장된 게 있으면 그대로 반환."""
        existing = self.blog_repo.find_by_festival_id(festival.kopis_id)
        if existing:
            return existing

        raw_results = self.naver_client.search(festival.search_keyword, display=3)
        blog_posts = [
            BlogPost(
                title=item["title"],
                link=item["link"],
                blogger_name=item["bloggername"],
                post_date=item["postdate"],
                festival_kopis_id=festival.kopis_id,
            )
            for item in raw_results
        ]

        if blog_posts:
            self.blog_repo.save_all(blog_posts)

        return blog_posts

    def refresh_blogs_for_festival(self, festival: Festival) -> list[BlogPost]:
        """기존 블로그 삭제 후 다시 검색"""
        self.blog_repo.delete_by_festival_id(festival.kopis_id)
        raw_results = self.naver_client.search(festival.search_keyword, display=3)
        blog_posts = [
            BlogPost(
                title=item["title"],
                link=item["link"],
                blogger_name=item["bloggername"],
                post_date=item["postdate"],
                festival_kopis_id=festival.kopis_id,
            )
            for item in raw_results
        ]
        if blog_posts:
            self.blog_repo.save_all(blog_posts)
        return blog_posts
