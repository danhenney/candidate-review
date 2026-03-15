from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Candidate, Evaluation, Rubric
from backend.schemas import EvaluationResponse, RubricCreate, RubricResponse
from backend.services.evaluator import get_pending_candidates, save_evaluation, build_evaluation_prompt, SYSTEM_PROMPT
from backend.services.rubric import get_active_rubric

router = APIRouter(tags=["evaluations"])


# --- Skill endpoints (Claude Code Max plan) ---

@router.get("/api/evaluate/pending")
def list_pending(db: Session = Depends(get_db)):
    """Get all pending candidates with their document text for Claude Code skill."""
    rubric = get_active_rubric(db)
    candidates = get_pending_candidates(db)

    # Build prompts for each candidate
    items = []
    for c in candidates:
        prompt = build_evaluation_prompt(rubric, c["document_text"])
        items.append({
            "id": c["id"],
            "name": c["name"],
            "prompt": prompt,
        })

    return {
        "system_prompt": SYSTEM_PROMPT,
        "rubric": rubric,
        "candidates": items,
        "count": len(items),
    }


class EvaluationSubmit(BaseModel):
    candidate_id: int
    result: dict


@router.post("/api/evaluate/submit")
def submit_evaluation(data: EvaluationSubmit, db: Session = Depends(get_db)):
    """Write evaluation result from Claude Code skill back to DB."""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="후보를 찾을 수 없습니다")

    rubric = get_active_rubric(db)
    save_evaluation(db, data.candidate_id, data.result, rubric)
    return {"message": f"'{candidate.name}' 평가 저장 완료", "candidate_id": data.candidate_id}


@router.post("/api/candidates/{candidate_id}/evaluate")
def trigger_evaluation(candidate_id: int, db: Session = Depends(get_db)):
    """Mark candidate as pending for Claude Code skill evaluation."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="후보를 찾을 수 없습니다")
    if not candidate.documents:
        raise HTTPException(status_code=400, detail="제출 서류가 없습니다")

    candidate.status = "pending"
    db.commit()
    return {"message": "평가 대기열에 추가되었습니다. Claude Code에서 /review-candidates 실행하세요.", "candidate_id": candidate_id}


@router.get("/api/evaluations/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="평가 결과를 찾을 수 없습니다")
    return evaluation


# --- Rubric endpoints ---

@router.get("/api/rubrics", response_model=list[RubricResponse])
def list_rubrics(db: Session = Depends(get_db)):
    return db.query(Rubric).order_by(Rubric.created_at.desc()).all()


@router.post("/api/rubrics", response_model=RubricResponse)
def create_rubric(data: RubricCreate, db: Session = Depends(get_db)):
    db.query(Rubric).update({"is_active": False})
    rubric = Rubric(name=data.name, dimensions=data.dimensions, is_active=True)
    db.add(rubric)
    db.commit()
    db.refresh(rubric)
    return rubric


@router.get("/api/rubrics/{rubric_id}", response_model=RubricResponse)
def get_rubric(rubric_id: int, db: Session = Depends(get_db)):
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="평가 기준을 찾을 수 없습니다")
    return rubric
