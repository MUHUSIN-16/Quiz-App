"""Response contracts for the public content APIs."""
from pydantic import BaseModel, Field


class ContentItem(BaseModel):
    id: str
    title: str


class UserItem(BaseModel):
    id: str
    name: str
    email: str


class ExamListResponse(BaseModel):
    exams: list[ContentItem]


class SubjectListResponse(BaseModel):
    subjects: list[ContentItem]


class ChapterListResponse(BaseModel):
    chapters: list[ContentItem]


class UserListResponse(BaseModel):
    users: list[UserItem]


class ErrorResponse(BaseModel):
    detail: str
