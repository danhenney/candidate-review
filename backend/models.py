from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from backend.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    notes = Column(Text, default="")
    status = Column(String, default="pending")  # pending | evaluating | completed | error
    created_at = Column(String, default=lambda: utcnow().isoformat())
    updated_at = Column(String, default=lambda: utcnow().isoformat())

    documents = relationship("Document", back_populates="candidate", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="candidate", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf | pptx | xlsx
    extracted_text = Column(Text, default="")
    created_at = Column(String, default=lambda: utcnow().isoformat())

    candidate = relationship("Candidate", back_populates="documents")


class Rubric(Base):
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, default="default")
    dimensions = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utcnow().isoformat())


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    rubric_id = Column(Integer, ForeignKey("rubrics.id"), nullable=True)
    overall_score = Column(Float, nullable=True)
    scores = Column(JSON, nullable=False)
    summary = Column(Text, default="")
    recommendation = Column(String, default="")  # 통과 | 검토 | 탈락
    strengths = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    raw_response = Column(Text, default="")
    model_used = Column(String, default="")
    tokens_used = Column(Integer, default=0)
    created_at = Column(String, default=lambda: utcnow().isoformat())

    candidate = relationship("Candidate", back_populates="evaluations")
