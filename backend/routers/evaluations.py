from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database import get_db, SessionLocal
from backend.models import Candidate, Evaluation, Rubric
from backend.schemas import EvaluationResponse, RubricCreate, RubricResponse
from backend.services.evaluator import evaluate_candidate

router = APIRouter(tags=["evaluations"])


def _run_evaluation(candidate_id: int):
    """Background task wrapper — creates its own DB session."""
    db = SessionLocal()
    try:
        evaluate_candidate(db, candidate_id)
    finally:
        db.close()


@router.post("/api/candidates/{candidate_id}/evaluate")
def trigger_evaluation(
    candidate_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="후보를 찾을 수 없습니다")
    if not candidate.documents:
        raise HTTPException(status_code=400, detail="제출 서류가 없습니다")
    if candidate.status == "evaluating":
        raise HTTPException(status_code=400, detail="평가가 이미 진행 중입니다")

    candidate.status = "evaluating"
    db.commit()

    background_tasks.add_task(_run_evaluation, candidate_id)
    return {"message": "평가가 시작되었습니다", "candidate_id": candidate_id}


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
    # Deactivate all existing rubrics
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
