from pydantic import BaseModel
from typing import Optional


class CandidateCreate(BaseModel):
    name: str
    notes: Optional[str] = ""


class CandidateResponse(BaseModel):
    id: int
    name: str
    notes: str
    status: str
    created_at: str
    updated_at: str
    documents: list = []
    evaluations: list = []

    class Config:
        from_attributes = True


class CandidateListItem(BaseModel):
    id: int
    name: str
    status: str
    created_at: str
    latest_score: Optional[float] = None
    recommendation: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    candidate_id: int
    filename: str
    file_type: str
    created_at: str

    class Config:
        from_attributes = True


class RubricCreate(BaseModel):
    name: str
    dimensions: list


class RubricResponse(BaseModel):
    id: int
    name: str
    dimensions: list
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    id: int
    candidate_id: int
    rubric_id: Optional[int] = None
    overall_score: Optional[float] = None
    scores: dict
    summary: str
    recommendation: str
    strengths: list
    risks: list
    model_used: str
    tokens_used: int
    created_at: str

    class Config:
        from_attributes = True
