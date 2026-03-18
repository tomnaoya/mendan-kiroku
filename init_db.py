"""
初回デプロイ時のDB初期化＆シードスクリプト
- テーブル作成（既存の場合はスキップ）
- スタッフデータ・サーベイデータ・面談記録の初期投入
"""
import json
import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal
from app.models import Base, Staff, SurveyRecord, InterviewRecord


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Staff).count() > 0:
            print("Data already seeded. Skipping.")
            return

        with open(os.path.join(os.path.dirname(__file__), "seed_data.json"), encoding="utf-8") as f:
            data = json.load(f)

        print(f"Seeding {len(data['staff'])} staff members...")

        # 3月データをname→recordのマップに
        march_map = {r['name']: r for r in data.get('march_surveys', [])}

        for item in data["staff"]:
            staff = Staff(name=item["name"], department=item["department"])
            db.add(staff)
            db.flush()

            # 2月サーベイ
            survey_feb = SurveyRecord(
                staff_id=staff.id,
                year=2026,
                month=2,
                score_work=item.get("score_work"),
                score_human=item.get("score_human"),
                score_health=item.get("score_health"),
                survey_comment=item.get("survey_comment", ""),
                response_date=parse_date(item.get("response_date", "")),
            )
            db.add(survey_feb)

            # 3月サーベイ（存在する人のみ）
            march = march_map.get(item["name"])
            if march:
                survey_mar = SurveyRecord(
                    staff_id=staff.id,
                    year=2026,
                    month=3,
                    score_work=march.get("score_work"),
                    score_human=march.get("score_human"),
                    score_health=march.get("score_health"),
                    survey_comment=march.get("survey_comment", ""),
                    response_date=parse_date(march.get("response_date", "")),
                )
                db.add(survey_mar)

            # 2月面談記録
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
