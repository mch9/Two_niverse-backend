from abc import ABC, abstractmethod
from app.domain.blog.entity import BlogPost


class BlogPostRepository(ABC):
    @abstractmethod
    def save_all(self, posts: list[BlogPost]) -> None:
        pass

    @abstractmethod
    def find_by_festival_id(self, festival_kopis_id: str) -> list[BlogPost]:
        pass

    @abstractmethod
    def delete_by_festival_id(self, festival_kopis_id: str) -> None:
        pass
