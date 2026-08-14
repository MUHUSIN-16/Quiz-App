"""Analytics calculated exclusively from immutable question-attempt events."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.db.mongo import db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/learning-velocity")
@router.get("/learning_velocity", include_in_schema=False)
def learning_velocity(limit: int = Query(default=50, ge=1, le=100)):
    """Rank learners: 60% accuracy, 25% speed, 15% time consistency (0-100)."""
    pipeline = [
        {"$group": {"_id": "$user_id", "attempts": {"$sum": 1},
                    "correct": {"$sum": {"$cond": ["$correct", 1, 0]}},
                    "avg_response_ms": {"$avg": "$duration_ms"},
                    "response_time_stddev_ms": {"$stdDevPop": "$duration_ms"}}},
        {"$lookup": {"from": "users", "localField": "_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
        {"$project": {"_id": 0, "user_id": "$_id", "user": {"$ifNull": ["$user.name", "Unknown user"]},
          "attempts": 1, "accuracy": {"$multiply": [{"$divide": ["$correct", "$attempts"]}, 100]},
          "avg_response_ms": 1, "consistency_ms": {"$ifNull": ["$response_time_stddev_ms", 0]}}},
    ]
    rows = list(db.attempts.aggregate(pipeline))
    for row in rows:
        # Speed is capped at a 60 second response; consistency is relative to pace.
        speed = max(0, 1 - min(row["avg_response_ms"], 60_000) / 60_000) * 25
        baseline = max(row["avg_response_ms"], 1)
        consistency = max(0, 1 - min(row["consistency_ms"] / baseline, 1)) * 15
        row["learning_velocity_index"] = round(row["accuracy"] * 0.60 + speed + consistency, 2)
        row["accuracy"] = round(row["accuracy"], 2)
        row["avg_response_ms"] = round(row["avg_response_ms"])
        row["consistency_ms"] = round(row["consistency_ms"])
    return {"formula": "accuracy*0.60 + speed*0.25 + consistency*0.15", "results": sorted(
        rows, key=lambda item: item["learning_velocity_index"], reverse=True)[:limit]}


@router.get("/fatigue")
def fatigue(quiz_id: str, window: int = Query(default=5, ge=1, le=20)):
    """Compare sequential question windows for exactly one quiz attempt."""
    quiz = db.quizzes.find_one({"_id": quiz_id}, {"_id": 1})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    pipeline = [
        {"$match": {"quiz_id": quiz_id}}, {"$sort": {"question_number": 1, "shown_at": 1}},
        {"$project": {"correct": 1, "duration_ms": 1, "question_number": 1,
                       "window": {"$floor": {"$divide": [{"$subtract": ["$question_number", 1]}, window]}}}},
        {"$group": {"_id": "$window", "questions": {"$sum": 1},
                    "correct": {"$sum": {"$cond": ["$correct", 1, 0]}},
                    "avg_response_ms": {"$avg": "$duration_ms"}}}, {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "window": {"$add": ["$_id", 1]}, "questions": 1,
          "accuracy": {"$multiply": [{"$divide": ["$correct", "$questions"]}, 100]}, "avg_response_ms": 1}},
    ]
    groups = list(db.attempts.aggregate(pipeline))
    for group in groups:
        group["accuracy"] = round(group["accuracy"], 2)
        group["avg_response_ms"] = round(group["avg_response_ms"])
        start = (group["window"] - 1) * window + 1
        group["range"] = f"Questions {start}-{start + group['questions'] - 1}"
    return {"quiz_id": quiz_id, "window_size": window, "groups": groups}


@router.get("/question-difficulty")
@router.get("/question_difficulty", include_in_schema=False)
def question_difficulty(limit: int = Query(default=50, ge=1, le=500), chapter_id: Optional[str] = None):
    """Rank questions by failure rate (70%) and response-time pressure (30%)."""
    match = {"chapter_id": chapter_id} if chapter_id else {}
    pipeline = [
        {"$match": match}, {"$group": {"_id": "$question_id", "total_attempts": {"$sum": 1},
          "correct": {"$sum": {"$cond": ["$correct", 1, 0]}}, "avg_response_ms": {"$avg": "$duration_ms"}}},
        {"$lookup": {"from": "questions", "localField": "_id", "foreignField": "_id", "as": "question"}},
        {"$unwind": {"path": "$question", "preserveNullAndEmptyArrays": True}},
        {"$project": {"_id": 0, "question_id": "$_id", "question": "$question.text", "total_attempts": 1,
          "accuracy": {"$multiply": [{"$divide": ["$correct", "$total_attempts"]}, 100]}, "avg_response_ms": 1}},
    ]
    rows = list(db.attempts.aggregate(pipeline))
    for row in rows:
        time_pressure = min(row["avg_response_ms"], 60_000) / 60_000
        row["difficulty_score"] = round((1 - row["accuracy"] / 100) * 70 + time_pressure * 30, 2)
        row["accuracy"] = round(row["accuracy"], 2)
        row["avg_response_ms"] = round(row["avg_response_ms"])
    return {"formula": "(1 - accuracy)*70 + normalized_response_time*30", "results": sorted(
        rows, key=lambda item: item["difficulty_score"], reverse=True)[:limit]}
