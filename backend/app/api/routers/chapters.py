from fastapi import APIRouter, HTTPException
from app.db.mongo import db
from app.schemas.api import ChapterListResponse, ContentItem, ErrorResponse

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("/", response_model=ChapterListResponse)
def list_chapters(subject_id: str = None):
    q = {} if not subject_id else {"subject_id": subject_id}
    items = list(db.chapters.find(q))
    for it in items:
        it["id"] = it.pop("_id")
    return {"chapters": items}


@router.get("/{chapter_id}", response_model=ContentItem, responses={404: {"model": ErrorResponse}})
def get_chapter(chapter_id: str):
    c = db.chapters.find_one({"_id": chapter_id})
    if not c:
        raise HTTPException(status_code=404, detail="Chapter not found")
    c["id"] = c.pop("_id")
    return c
