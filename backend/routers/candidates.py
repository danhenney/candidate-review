from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Candidate
from backend.schemas import CandidateCreate, CandidateResponse, CandidateListItem

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.post("", response_model=CandidateResponse)
def create_candidate(data: CandidateCreate, db: Session = Depends(get_db)):
    candidate = Candidate(name=data.name, notes=data.notes or "")
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("")
def list_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    result = []
    for c in candidates:
        latest_eval = c.evaluations[-1] if c.evaluations else None
        result.append(
            CandidateListItem(
                id=c.id,
                name=c.name,
                status=c.status,
                created_at=c.created_at,
                latest_score=latest_eval.overall_score if latest_eval else None,
                recommendation=latest_eval.recommendation if latest_eval else None,
            )
        )
    return result


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="후보를 찾을 수 없습니다")
    return candidate


@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="후보를 찾을 수 없습니다")
    db.delete(candidate)
    db.commit()
    return {"message": "삭제 완료"}
