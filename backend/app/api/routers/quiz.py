"""Quiz lifecycle endpoints.

The quiz document is the source of truth for progression.  Keeping the question
order and current position here makes it impossible for a client to skip ahead
or revisit a submitted question by calling the API directly.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db.mongo import db

router = APIRouter(prefix="/quiz", tags=["quiz"])
DEFAULT_QUESTION_COUNT = 10


class StartQuizRequest(BaseModel):
    user_id: str = Field(min_length=1)
    exam_id: Optional[str] = None
    subject_id: Optional[str] = None
    chapter_id: Optional[str] = None
    question_count: int = Field(default=DEFAULT_QUESTION_COUNT, ge=1, le=50)


def _question_filter(payload: StartQuizRequest) -> tuple[dict, dict]:
    """Validate scope and return the filter plus normalized hierarchy IDs."""
    if not db.users.find_one({"_id": payload.user_id}, {"_id": 1}):
        raise HTTPException(status_code=404, detail="User not found")

    scope = {"exam_id": payload.exam_id, "subject_id": payload.subject_id, "chapter_id": payload.chapter_id}
    if payload.chapter_id:
        chapter = db.chapters.find_one({"_id": payload.chapter_id})
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        subject = db.subjects.find_one({"_id": chapter["subject_id"]})
        if not subject:
            raise HTTPException(status_code=409, detail="Chapter has no valid subject")
        scope.update(exam_id=subject["exam_id"], subject_id=subject["_id"])
        return {"chapter_id": chapter["_id"]}, scope

    if payload.subject_id:
        subject = db.subjects.find_one({"_id": payload.subject_id})
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        scope.update(exam_id=subject["exam_id"], subject_id=subject["_id"])
        chapter_ids = [c["_id"] for c in db.chapters.find({"subject_id": subject["_id"]}, {"_id": 1})]
        return {"chapter_id": {"$in": chapter_ids}}, scope

    if payload.exam_id:
        if not db.exams.find_one({"_id": payload.exam_id}, {"_id": 1}):
            raise HTTPException(status_code=404, detail="Exam not found")
        subject_ids = [s["_id"] for s in db.subjects.find({"exam_id": payload.exam_id}, {"_id": 1})]
        chapter_ids = [c["_id"] for c in db.chapters.find({"subject_id": {"$in": subject_ids}}, {"_id": 1})]
        return {"chapter_id": {"$in": chapter_ids}}, scope

    raise HTTPException(status_code=422, detail="Choose an exam, subject, or chapter")


@router.post("/start", status_code=201)
def start_quiz(payload: StartQuizRequest):
    question_filter, scope = _question_filter(payload)
    question_ids = [q["_id"] for q in db.questions.aggregate([
        {"$match": question_filter}, {"$sample": {"size": payload.question_count}}, {"$project": {"_id": 1}}
    ])]
    if not question_ids:
        raise HTTPException(status_code=404, detail="No questions available for this selection")

    quiz_id = str(uuid4())
    db.quizzes.insert_one({
        "_id": quiz_id, "user_id": payload.user_id, **scope,
        "question_ids": question_ids, "current_index": 0, "status": "in_progress",
        "started_at": datetime.now(timezone.utc), "completed_at": None,
    })
    return {"quiz_id": quiz_id, "question_count": len(question_ids)}


@router.get("/{quiz_id}/next")
def next_question(quiz_id: str):
    quiz = db.quizzes.find_one({"_id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz["status"] == "completed" or quiz["current_index"] >= len(quiz["question_ids"]):
        return {"done": True}

    index = quiz["current_index"]
    question_id = quiz["question_ids"][index]
    question = db.questions.find_one({"_id": question_id})
    if not question:
        raise HTTPException(status_code=409, detail="Quiz question no longer exists")

    shown_at = quiz.get("shown_at")
    # Persist the first server-side display time so duration cannot be forged.
    if quiz.get("shown_question_id") != question_id or not shown_at:
        shown_at = datetime.now(timezone.utc)
        db.quizzes.update_one({"_id": quiz_id, "current_index": index}, {"$set": {
            "shown_question_id": question_id, "shown_at": shown_at
        }})
    return {
        "question_id": question["_id"], "text": question["text"], "options": question["options"],
        "position": index + 1, "total_questions": len(quiz["question_ids"]), "shown_at": shown_at,
    }


@router.get("/{quiz_id}/result")
def quiz_result(quiz_id: str):
    quiz = db.quizzes.find_one({"_id": quiz_id}, {"question_ids": 1, "status": 1, "subject_id": 1, "chapter_id": 1})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    attempts = list(db.attempts.find({"quiz_id": quiz_id}, {"correct": 1, "duration_ms": 1}))
    answered = len(attempts)
    correct = sum(1 for attempt in attempts if attempt["correct"])
    return {"quiz_id": quiz_id, "status": quiz["status"], "subject_id": quiz.get("subject_id"),
            "chapter_id": quiz.get("chapter_id"), "total_questions": len(quiz["question_ids"]),
            "answered": answered, "correct": correct, "score": correct,
            "accuracy": round((correct / answered) * 100, 1) if answered else 0,
            "avg_response_ms": round(sum(a["duration_ms"] for a in attempts) / answered) if answered else 0}
