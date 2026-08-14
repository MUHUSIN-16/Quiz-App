from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pymongo import ReturnDocument

from app.db.mongo import db

router = APIRouter(prefix="/submit", tags=["submit"])


class SubmitRequest(BaseModel):
    quiz_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    question_id: str = Field(min_length=1)
    selected_option: int = Field(ge=0, le=3)


@router.post("/")
def submit_answer(payload: SubmitRequest):
    quiz = db.quizzes.find_one({"_id": payload.quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz["user_id"] != payload.user_id:
        raise HTTPException(status_code=403, detail="Quiz belongs to another user")
    if quiz["status"] != "in_progress" or quiz["current_index"] >= len(quiz["question_ids"]):
        raise HTTPException(status_code=409, detail="Quiz is already complete")
    expected_id = quiz["question_ids"][quiz["current_index"]]
    if payload.question_id != expected_id or quiz.get("shown_question_id") != expected_id:
        raise HTTPException(status_code=409, detail="Submit the currently displayed question")

    question = db.questions.find_one({"_id": expected_id})
    if not question:
        raise HTTPException(status_code=409, detail="Question no longer exists")
    if payload.selected_option >= len(question["options"]):
        raise HTTPException(status_code=422, detail="Selected option is out of range")

    submitted_at = datetime.now(timezone.utc)
    shown_at = quiz["shown_at"]
    if shown_at.tzinfo is None:
        shown_at = shown_at.replace(tzinfo=timezone.utc)
    duration_ms = max(0, int((submitted_at - shown_at).total_seconds() * 1000))
    correct = payload.selected_option == question["correct_option"]
    position = quiz["current_index"] + 1
    completed = position == len(quiz["question_ids"])

    # Conditional write prevents duplicate concurrent submissions of one question.
    updated = db.quizzes.find_one_and_update(
        {"_id": payload.quiz_id, "current_index": quiz["current_index"], "shown_question_id": expected_id},
        {"$inc": {"current_index": 1}, "$set": {"shown_question_id": None, "shown_at": None,
         "status": "completed" if completed else "in_progress",
         "completed_at": submitted_at if completed else None}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=409, detail="This question was already submitted")
    db.attempts.insert_one({
        "_id": str(uuid4()), "user_id": payload.user_id, "quiz_id": payload.quiz_id,
        "question_id": expected_id, "exam_id": quiz.get("exam_id"), "subject_id": quiz.get("subject_id"),
        "chapter_id": question["chapter_id"], "question_number": position, "shown_at": shown_at,
        "submitted_at": submitted_at, "duration_ms": duration_ms, "selected_option": payload.selected_option,
        "correct": correct,
    })
    return {"correct": correct, "duration_ms": duration_ms, "position": position, "done": completed}
