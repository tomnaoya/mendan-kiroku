"""
DB初期化＆シードスクリプト
- テーブル作成
- スタッフ・2月サーベイ・面談記録の初期投入（初回のみ）
- 3月サーベイは常に差分追加（既存レコードはスキップ）
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal
from app.models import Base, Staff, SurveyRecord, InterviewRecord


def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        with open(os.path.join(os.path.dirname(__file__), "seed_data.json"), encoding="utf-8") as f:
            data = json.load(f)

        march_map = {r["name"]: r for r in data.get("march_surveys", [])}

        # ── 初回のみ: スタッフ・2月データ投入 ──
        if db.query(Staff).count() == 0:
            print(f"Initial seed: {len(data['staff'])} staff members...")
            for item in data["staff"]:
                staff = Staff(name=item["name"], department=item["department"])
                db.add(staff)
                db.flush()

                db.add(SurveyRecord(
                    staff_id=staff.id, year=2026, month=2,
                    score_work=item.get("score_work"),
                    score_human=item.get("score_human"),
                    score_health=item.get("score_health"),
                    survey_comment=item.get("survey_comment", ""),
                    response_date=parse_date(item.get("response_date", "")),
                ))

                interview_data = data["interviews"].get(item["name"])
                if interview_data and interview_data.get("content"):
                    db.add(InterviewRecord(
                        staff_id=staff.id, year=2026, month=2,
                        interview_date=parse_date(interview_data.get("interview_date", "")),
                        q1_content=interview_data.get("content", ""),
                    ))

            db.commit()
            print("Initial seed complete.")
        else:
            print("Staff already exists. Skipping initial seed.")

        # ── 毎回実行: 3月サーベイの差分追加 ──
        added = 0
        for name, march in march_map.items():
            staff = db.query(Staff).filter(Staff.name == name).first()
            if not staff:
                continue
            exists = db.query(SurveyRecord).filter(
                SurveyRecord.staff_id == staff.id,
                SurveyRecord.year == 2026,
                SurveyRecord.month == 3,
            ).first()
            if not exists:
                db.add(SurveyRecord(
                    staff_id=staff.id, year=2026, month=3,
                    score_work=march.get("score_work"),
                    score_human=march.get("score_human"),
                    score_health=march.get("score_health"),
                    survey_comment=march.get("survey_comment", ""),
                    response_date=parse_date(march.get("response_date", "")),
                ))
                added += 1

        db.commit()
        print(f"March survey: {added} records added.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
