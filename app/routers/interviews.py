import os
from datetime import date
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import InterviewRecord

router = APIRouter()


def require_login(request: Request):
    return request.session.get("logged_in")


@router.post("/interviews/save")
async def save_interview(
    request: Request,
    staff_id: int = Form(...),
    year: int = Form(...),
    month: int = Form(...),
    interview_date: str = Form(""),
    interviewer: str = Form(""),
    location: str = Form(""),
    duration: str = Form(""),
    q1_content: str = Form(""),
    q2_content: str = Form(""),
    q3_content: str = Form(""),
    overall_findings: str = Form(""),
    improvement_policy: str = Form(""),
    other_notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=302)

    parsed_date = None
    if interview_date:
        try:
            parsed_date = date.fromisoformat(interview_date)
        except ValueError:
            pass

    record = (
        db.query(InterviewRecord)
        .filter(InterviewRecord.staff_id == staff_id, InterviewRecord.year == year, InterviewRecord.month == month)
        .first()
    )

    if record:
        record.interview_date = parsed_date
        record.interviewer = interviewer
        record.location = location
        record.duration = duration
        record.q1_content = q1_content
        record.q2_content = q2_content
        record.q3_content = q3_content
        record.overall_findings = overall_findings
        record.improvement_policy = improvement_policy
        record.other_notes = other_notes
    else:
        record = InterviewRecord(
            staff_id=staff_id,
            year=year,
            month=month,
            interview_date=parsed_date,
            interviewer=interviewer,
            location=location,
            duration=duration,
            q1_content=q1_content,
            q2_content=q2_content,
            q3_content=q3_content,
            overall_findings=overall_findings,
            improvement_policy=improvement_policy,
            other_notes=other_notes,
        )
        db.add(record)

    db.commit()
    return RedirectResponse(url=f"/staff/{staff_id}?year={year}&month={month}", status_code=302)
