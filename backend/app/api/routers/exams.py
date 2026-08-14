from fastapi import APIRouter, HTTPException
from app.db.mongo import db
from app.schemas.api import ContentItem, ExamListResponse, ErrorResponse

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get("/", response_model=ExamListResponse)
def list_exams():
    items = list(db.exams.find({}))
    for it in items:
        it["id"] = it.pop("_id")
    return {"exams": items}


@router.get("/{exam_id}", response_model=ContentItem, responses={404: {"model": ErrorResponse}})
def get_exam(exam_id: str):
    e = db.exams.find_one({"_id": exam_id})
    if not e:
        raise HTTPException(status_code=404, detail="Exam not found")
    e["id"] = e.pop("_id")
    return e
