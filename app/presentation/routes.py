from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    festival_service = current_app.config["FESTIVAL_SERVICE"]

    # 필터 파라미터 수집
    keyword = request.args.get("keyword", "").strip()
    area = request.args.get("area", "").strip()
    start_date_str = request.args.get("start_date", "").strip()
    end_date_str = request.args.get("end_date", "").strip()
    festival_only = request.args.get("festival_only") == "on"

    # 날짜 파싱
    start_date = None
    end_date = None
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    # 필터가 하나라도 있으면 검색, 없으면 전체
    has_filter = keyword or area or start_date or end_date or festival_only
    if has_filter:
        festivals = festival_service.search_festivals(
            keyword=keyword or None,
            area=area or None,
            start_date=start_date,
            end_date=end_date,
            festival_only=festival_only,
        )
    else:
        festivals = festival_service.get_all_festivals()

    areas = festival_service.get_all_areas()

    return render_template(
        "index.html",
        festivals=festivals,
        areas=areas,
        filters={
            "keyword": keyword,
            "area": area,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "festival_only": festival_only,
        },
    )


@bp.route("/festivals/<kopis_id>")
def festival_detail(kopis_id):
    festival_service = current_app.config["FESTIVAL_SERVICE"]
    blog_service = current_app.config["BLOG_SERVICE"]

    festival = festival_service.get_festival_detail(kopis_id)
    if not festival:
        flash("페스티벌을 찾을 수 없습니다.", "error")
        return redirect(url_for("main.index"))

    blogs = blog_service.fetch_blogs_for_festival(festival)
    return render_template("detail.html", festival=festival, blogs=blogs)
