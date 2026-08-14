import pytest
from fastapi import HTTPException

from app.api.routers import analytics, exams, quiz, submit


class FakeCollection:
    def __init__(self, items=None, aggregate_rows=None):
        self.items = items or {}
        self.aggregate_rows = aggregate_rows or []

    def find_one(self, query, *args, **kwargs):
        return self.items.get(query.get("_id"))

    def aggregate(self, pipeline):
        return self.aggregate_rows


class FakeDb:
    def __init__(self):
        self.users = FakeCollection({"u1": {"_id": "u1", "name": "Ava Patel"}})
        self.attempts = FakeCollection()
        self.quizzes = FakeCollection()
        self.questions = FakeCollection()


def test_exam_detail_returns_404_for_unknown_exam(monkeypatch):
    monkeypatch.setattr(exams, "db", type("Db", (), {"exams": FakeCollection()})())
    with pytest.raises(HTTPException) as error:
        exams.get_exam("missing")
    assert error.value.status_code == 404
    assert error.value.detail == "Exam not found"


def test_submit_rejects_any_question_except_current_one(monkeypatch):
    database = FakeDb()
    database.quizzes = FakeCollection({"quiz-1": {
        "_id": "quiz-1", "user_id": "u1", "status": "in_progress",
        "current_index": 0, "question_ids": ["question-1"], "shown_question_id": "question-1",
    }})
    monkeypatch.setattr(submit, "db", database)
    with pytest.raises(HTTPException) as error:
        submit.submit_answer(submit.SubmitRequest(quiz_id="quiz-1", user_id="u1", question_id="other", selected_option=0))
    assert error.value.status_code == 409
    assert error.value.detail == "Submit the currently displayed question"


def test_learning_velocity_returns_ranked_contract(monkeypatch):
    database = FakeDb()
    database.attempts = FakeCollection(aggregate_rows=[{
        "user_id": "u1", "user": "Ava Patel", "attempts": 4, "accuracy": 75.0,
        "avg_response_ms": 12000.0, "consistency_ms": 3000.0,
    }])
    monkeypatch.setattr(analytics, "db", database)
    response = analytics.learning_velocity(limit=10)
    row = response["results"][0]
    assert response["formula"]
    assert row["user"] == "Ava Patel"
    assert set(["accuracy", "avg_response_ms", "consistency_ms", "learning_velocity_index"]).issubset(row)
