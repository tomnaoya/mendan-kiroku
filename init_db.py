"""
初回デプロイ時のDB初期化＆シードスクリプト
- テーブル作成（既存の場合はスキップ）
- スタッフデータ・サーベイデータ・面談記録の初期投入
"""
import json
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal
from app.models import Base, Staff, SurveyRecord, InterviewRecord


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d"):
        try:
            from datetime import datetime
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(Staff).count() > 0:
            print("Data already seeded. Skipping.")
            return

        with open(os.path.join(os.path.dirname(__file__), "seed_data.json"), encoding="utf-8") as f:
            data = json.load(f)

        print(f"Seeding {len(data['staff'])} staff members...")

        for item in data["staff"]:
            staff = Staff(name=item["name"], department=item["department"])
            db.add(staff)
            db.flush()

            # Survey record for 2026/02
            survey = SurveyRecord(
                staff_id=staff.id,
                year=2026,
                month=2,
                score_work=item.get("score_work"),
                score_human=item.get("score_human"),
                score_health=item.get("score_health"),
                survey_comment=item.get("survey_comment", ""),
                response_date=parse_date(item.get("response_date", "")),
            )
            db.add(survey)

            # Interview record if available
            interview_data = data["interviews"].get(item["name"])
            if interview_data and interview_data.get("content"):
                interview = InterviewRecord(
                    staff_id=staff.id,
                    year=2026,
                    month=2,
                    interview_date=parse_date(interview_data.get("interview_date", "")),
                    q1_content=interview_data.get("content", ""),
                )
                db.add(interview)

        db.commit()
        print("Seed complete.")

    except Exception as e:
        db.rollback()
        print(f"Error during seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
