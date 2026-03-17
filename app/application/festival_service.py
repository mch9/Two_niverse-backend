import os
import time
import requests

from app.domain.festival.entity import Festival
from app.domain.festival.repository import FestivalRepository
from app.infrastructure.external_api.kopis_client import KopisClient


class FestivalApplicationService:
    def __init__(
        self,
        festival_repo: FestivalRepository,
        kopis_client: KopisClient,
        poster_dir: str,
    ):
        self.festival_repo = festival_repo
        self.kopis_client = kopis_client
        self.poster_dir = poster_dir

    def collect_festivals(self, keyword: str, stdate: str, eddate: str) -> int:
        """KOPIS에서 페스티벌 검색 → 상세 조회 → DB 저장. 수집 건수 반환."""
        summary_list = self.kopis_client.search_festivals(keyword, stdate, eddate)
        count = 0

        for item in summary_list:
            time.sleep(0.3)
            festival = self.kopis_client.get_festival_detail(item["kopis_id"])

            # 포스터 다운로드
            if festival.poster_url:
                local_path = self._download_poster(festival.kopis_id, festival.poster_url)
                festival.local_poster_path = local_path

            self.festival_repo.save(festival)
            count += 1

        return count

    def get_all_festivals(self) -> list[Festival]:
        return self.festival_repo.find_all()

    def search_festivals(
        self,
        keyword: str | None = None,
        area: str | None = None,
        start_date=None,
        end_date=None,
        festival_only: bool = False,
    ) -> list[Festival]:
        return self.festival_repo.search(
            keyword=keyword,
            area=area,
            start_date=start_date,
            end_date=end_date,
            festival_only=festival_only,
        )

    def get_all_areas(self) -> list[str]:
        return self.festival_repo.get_all_areas()

    def get_festival_detail(self, kopis_id: str) -> Festival | None:
        return self.festival_repo.find_by_kopis_id(kopis_id)

    def _download_poster(self, kopis_id: str, poster_url: str) -> str | None:
        """포스터 이미지를 다운로드하고 로컬 경로 반환"""
        try:
            resp = requests.get(poster_url, timeout=15)
            resp.raise_for_status()

            ext = poster_url.rsplit(".", 1)[-1].lower()
            if ext not in ("jpg", "jpeg", "png", "gif"):
                ext = "jpg"
            filename = f"{kopis_id}.{ext}"
            filepath = os.path.join(self.poster_dir, filename)

            os.makedirs(self.poster_dir, exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(resp.content)

            return filename
        except Exception:
            return None
