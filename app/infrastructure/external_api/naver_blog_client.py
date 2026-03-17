import re
import urllib.parse

import requests


class NaverBlogClient:
    BASE_URL = "https://openapi.naver.com/v1/search/blog.json"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def search(self, query: str, display: int = 3, sort: str = "sim") -> list[dict]:
        """네이버 블로그 검색. 반환: [{'title', 'link', 'bloggername', 'postdate'}, ...]"""
        encoded = urllib.parse.quote(query)
        url = f"{self.BASE_URL}?query={encoded}&display={display}&sort={sort}"

        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        results = []
        for item in data.get("items", []):
            title = self._strip_html(item.get("title", ""))
            results.append({
                "title": title,
                "link": item.get("link", ""),
                "bloggername": item.get("bloggername", ""),
                "postdate": item.get("postdate", ""),
            })
        return results

    def _strip_html(self, text: str) -> str:
        """HTML 태그 제거"""
        return re.sub(r"<[^>]+>", "", text)
