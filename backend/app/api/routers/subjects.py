from fastapi import APIRouter, HTTPException
from app.db.mongo import db
from app.schemas.api import ContentItem, ErrorResponse, SubjectListResponse

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("/", response_model=SubjectListResponse)
def list_subjects(exam_id: str = None):
    q = {} if not exam_id else {"exam_id": exam_id}
    items = list(db.subjects.find(q))
    for it in items:
        it["id"] = it.pop("_id")
    return {"subjects": items}


@router.get("/{subject_id}", response_model=ContentItem, responses={404: {"model": ErrorResponse}})
def get_subject(subject_id: str):
    s = db.subjects.find_one({"_id": subject_id})
    if not s:
        raise HTTPException(status_code=404, detail="Subject not found")
    s["id"] = s.pop("_id")
    return s
