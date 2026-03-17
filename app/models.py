from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)

    survey_records = relationship("SurveyRecord", back_populates="staff", order_by="SurveyRecord.year, SurveyRecord.month")
    interview_records = relationship("InterviewRecord", back_populates="staff", order_by="InterviewRecord.year, InterviewRecord.month")


class SurveyRecord(Base):
    __tablename__ = "survey_records"
    __table_args__ = (UniqueConstraint("staff_id", "year", "month"),)

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    score_work = Column(Integer)
    score_human = Column(Integer)
    score_health = Column(Integer)
    survey_comment = Column(Text, default="")
    response_date = Column(Date, nullable=True)

    staff = relationship("Staff", back_populates="survey_records")

    @property
    def min_score(self):
        scores = [s for s in [self.score_work, self.score_human, self.score_health] if s is not None]
        return min(scores) if scores else None

    @property
    def avg_score(self):
        scores = [s for s in [self.score_work, self.score_human, self.score_health] if s is not None]
        return round(sum(scores) / len(scores), 2) if scores else None


class InterviewRecord(Base):
    __tablename__ = "interview_records"
    __table_args__ = (UniqueConstraint("staff_id", "year", "month"),)

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    interview_date = Column(Date, nullable=True)
    interviewer = Column(String(100), default="")
    location = Column(String(200), default="")
    duration = Column(String(100), default="")
    q1_content = Column(Text, default="")
    q2_content = Column(Text, default="")
    q3_content = Column(Text, default="")
    overall_findings = Column(Text, default="")
    improvement_policy = Column(Text, default="")
    other_notes = Column(Text, default="")

    staff = relationship("Staff", back_populates="interview_records")
