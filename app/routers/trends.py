import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Staff, SurveyRecord

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))


def require_login(request: Request):
    return request.session.get("logged_in")


@router.get("/trends", response_class=HTMLResponse)
async def trends(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=302)

    # 全月リスト
    months_q = (
        db.query(SurveyRecord.year, SurveyRecord.month)
        .distinct()
        .order_by(SurveyRecord.year, SurveyRecord.month)
        .all()
    )
    month_labels = [f"{y}/{m:02d}" for y, m in months_q]

    # 全体平均（月別）
    def avg_or_none(val):
        return round(val, 2) if val is not None else None

    overall = []
    for y, m in months_q:
        row = db.query(
            func.avg(SurveyRecord.score_work),
            func.avg(SurveyRecord.score_human),
            func.avg(SurveyRecord.score_health),
            func.count(SurveyRecord.id),
        ).filter(SurveyRecord.year == y, SurveyRecord.month == m).first()
        work, human, health, cnt = row
        avg_total = None
        scores = [x for x in [work, human, health] if x is not None]
        if scores:
            avg_total = round(sum(scores) / len(scores), 2)
        overall.append({
            "label": f"{y}/{m:02d}",
            "work": avg_or_none(work),
            "human": avg_or_none(human),
            "health": avg_or_none(health),
            "total": avg_total,
            "count": cnt,
        })

    # 所属院リスト
    all_staff = db.query(Staff).all()
    departments = sorted(set(s.department for s in all_staff))

    # 院別平均（月別）
    dept_data = {}
    for dept in departments:
        staff_ids = [s.id for s in all_staff if s.department == dept]
        rows = []
        for y, m in months_q:
            row = db.query(
                func.avg(SurveyRecord.score_work),
                func.avg(SurveyRecord.score_human),
                func.avg(SurveyRecord.score_health),
                func.count(SurveyRecord.id),
            ).filter(
                SurveyRecord.staff_id.in_(staff_ids),
                SurveyRecord.year == y,
                SurveyRecord.month == m,
            ).first()
            work, human, health, cnt = row
            scores = [x for x in [work, human, health] if x is not None]
            avg_total = round(sum(scores) / len(scores), 2) if scores else None
            rows.append({
                "label": f"{y}/{m:02d}",
                "work": avg_or_none(work),
                "human": avg_or_none(human),
                "health": avg_or_none(health),
                "total": avg_total,
                "count": cnt,
            })
        dept_data[dept] = rows

    return templates.TemplateResponse("trends.html", {
        "request": request,
        "month_labels": month_labels,
        "overall": overall,
        "departments": departments,
        "dept_data": dept_data,
    })
