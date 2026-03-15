import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.config import UPLOAD_DIR
from backend.database import get_db
from backend.models import Candidate, Document
from backend.schemas import DocumentResponse
from backend.services.document_parser import extract_text

router = APIRouter(prefix="/api/candidates", tags=["uploads"])

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-excel": "xls",
}


@router.post("/{candidate_id}/documents", response_model=list[DocumentResponse])
async def upload_documents(
    candidate_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="후보를 찾을 수 없습니다")

    uploaded = []
    for file in files:
        # Determine file type from extension as fallback
        ext = os.path.splitext(file.filename or "")[1].lower().lstrip(".")
        file_type = ALLOWED_TYPES.get(file.content_type)
        if not file_type:
            ext_map = {"pdf": "pdf", "pptx": "pptx", "xlsx": "xlsx", "xls": "xls"}
            file_type = ext_map.get(ext)
        if not file_type:
            continue  # Skip unsupported files

        # Save file
        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Extract text
        extracted = extract_text(file_path, file_type)

        doc = Document(
            candidate_id=candidate_id,
            filename=file.filename or "unknown",
            file_path=file_path,
            file_type=file_type,
            extracted_text=extracted,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        uploaded.append(doc)

    return uploaded


@router.get("/{candidate_id}/documents", response_model=list[DocumentResponse])
def list_documents(candidate_id: int, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.candidate_id == candidate_id).all()
    return docs


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="서류를 찾을 수 없습니다")
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc)
    db.commit()
    return {"message": "삭제 완료"}
