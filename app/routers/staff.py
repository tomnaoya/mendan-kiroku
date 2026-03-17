import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Staff, SurveyRecord, InterviewRecord

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))


def require_login(request: Request):
    if not request.session.get("logged_in"):
        return None
    return True


@router.get("/staff", response_class=HTMLResponse)
async def staff_list(request: Request, dept: str = "", db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=302)

    staff_query = db.query(Staff).order_by(Staff.department, Staff.name)
    all_staff = staff_query.all()

    departments = sorted(set(s.department for s in all_staff))

    # Attach latest survey record to each staff
    staff_data = []
    for s in all_staff:
        if dept and s.department != dept:
            continue
        latest = (
            db.query(SurveyRecord)
            .filter(SurveyRecord.staff_id == s.id)
            .order_by(SurveyRecord.year.desc(), SurveyRecord.month.desc())
            .first()
        )
        has_interview = db.query(InterviewRecord).filter(InterviewRecord.staff_id == s.id).count() > 0
        staff_data.append({
            "staff": s,
            "latest_survey": latest,
            "has_interview": has_interview,
        })

    return templates.TemplateResponse("list.html", {
        "request": request,
        "staff_data": staff_data,
        "departments": departments,
        "selected_dept": dept,
    })


@router.get("/staff/{staff_id}", response_class=HTMLResponse)
async def staff_detail(
    request: Request,
    staff_id: int,
    year: int = 2026,
    month: int = 2,
    db: Session = Depends(get_db),
):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=302)

    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        return RedirectResponse(url="/staff", status_code=302)

    survey_records = (
        db.query(SurveyRecord)
        .filter(SurveyRecord.staff_id == staff_id)
        .order_by(SurveyRecord.year, SurveyRecord.month)
        .all()
    )

    # Chart data
    chart_labels = [f"{r.year}/{r.month:02d}" for r in survey_records]
    chart_work = [r.score_work for r in survey_records]
    chart_human = [r.score_human for r in survey_records]
    chart_health = [r.score_health for r in survey_records]

    # Selected month survey
    selected_survey = (
        db.query(SurveyRecord)
        .filter(SurveyRecord.staff_id == staff_id, SurveyRecord.year == year, SurveyRecord.month == month)
        .first()
    )

    # Selected month interview
    selected_interview = (
        db.query(InterviewRecord)
        .filter(InterviewRecord.staff_id == staff_id, InterviewRecord.year == year, InterviewRecord.month == month)
        .first()
    )

    # Available months (union of survey and interview months)
    survey_months = [(r.year, r.month) for r in survey_records]
    interview_months = [
        (r.year, r.month)
        for r in db.query(InterviewRecord).filter(InterviewRecord.staff_id == staff_id).all()
    ]
    available_months = sorted(set(survey_months + interview_months), reverse=True)

    return templates.TemplateResponse("detail.html", {
        "request": request,
        "staff": staff,
        "survey_records": survey_records,
        "chart_labels": chart_labels,
        "chart_work": chart_work,
        "chart_human": chart_human,
        "chart_health": chart_health,
        "selected_year": year,
        "selected_month": month,
        "selected_survey": selected_survey,
        "selected_interview": selected_interview,
        "available_months": available_months,
    })
