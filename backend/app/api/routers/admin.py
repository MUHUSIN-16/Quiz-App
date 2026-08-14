from fastapi import APIRouter
from app.db.mongo import db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/create_indexes")
def create_indexes():
    col = db.attempts
    created = []
    created.append(col.create_index([("user_id", 1), ("submitted_at", -1)], name="user_submitted"))
    created.append(col.create_index([("question_id", 1)], name="question"))
    created.append(col.create_index([("quiz_id", 1), ("question_number", 1)], name="quiz_sequence"))
    created.append(col.create_index([("chapter_id", 1), ("question_id", 1)], name="chapter_question"))
    created.append(db.questions.create_index([("chapter_id", 1)], name="question_chapter"))
    created.append(db.subjects.create_index([("exam_id", 1)], name="subject_exam"))
    created.append(db.chapters.create_index([("subject_id", 1)], name="chapter_subject"))
    return {"created_indexes": created}
