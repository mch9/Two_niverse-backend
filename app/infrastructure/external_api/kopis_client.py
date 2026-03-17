import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

from app.domain.festival.entity import Festival
from app.domain.festival.value_objects import Period, TicketLink


class KopisClient:
    BASE_URL = "http://www.kopis.or.kr/openApi/restful/pblprfr"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_festivals(self, keyword: str, stdate: str, eddate: str) -> list[dict]:
        """KOPIS에서 페스티벌 목록 검색. 반환: [{'kopis_id': ..., 'name': ...}, ...]"""
        encoded = urllib.parse.quote(keyword)
        url = (
            f"{self.BASE_URL}?service={self.api_key}"
            f"&stdate={stdate}&eddate={eddate}"
            f"&cpage=1&rows=100&shprfnm={encoded}"
            f"&shcate=CCCD"
        )
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        results = []
        for db in root.findall("db"):
            kopis_id = self._text(db, "mt20id")
            name = self._text(db, "prfnm")
            if kopis_id and name:
                results.append({"kopis_id": kopis_id, "name": name})
        return results

    def get_festival_detail(self, kopis_id: str) -> Festival:
        """KOPIS에서 공연 상세 조회 후 Festival 도메인 엔티티로 반환"""
        url = f"{self.BASE_URL}/{kopis_id}?service={self.api_key}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        db = root.find("db")

        start_date = self._parse_date(self._text(db, "prfpdfrom"))
        end_date = self._parse_date(self._text(db, "prfpdto"))

        # ticket links 파싱
        ticket_links = []
        for relate in db.findall(".//relate"):
            vendor = self._text(relate, "relatenm")
            link_url = self._text(relate, "relateurl")
            if vendor and link_url:
                ticket_links.append(TicketLink(vendor_name=vendor, url=link_url))

        festival_flag = self._text(db, "festival")

        return Festival(
            kopis_id=self._text(db, "mt20id"),
            name=self._text(db, "prfnm"),
            period=Period(start_date=start_date, end_date=end_date),
            venue=self._text(db, "fcltynm") or "",
            area=self._text(db, "area") or "",
            genre=self._text(db, "genrenm") or "",
            age_limit=self._text(db, "prfage"),
            price_info=self._text(db, "pcseguidance"),
            poster_url=self._text(db, "poster"),
            schedule=self._text(db, "dtguidance"),
            cast_info=self._text(db, "prfcast"),
            producer=self._text(db, "entrpsnmH"),
            is_festival=(festival_flag == "Y"),
            ticket_links=ticket_links,
        )

    def _text(self, element, tag: str) -> str | None:
        """XML 요소에서 텍스트 추출. 비어있으면 None 반환"""
        el = element.find(tag)
        if el is not None and el.text and el.text.strip():
            return el.text.strip()
        return None

    def _parse_date(self, date_str: str):
        """KOPIS 날짜 형식(YYYY.MM.DD) 파싱"""
        return datetime.strptime(date_str, "%Y.%m.%d").date()
