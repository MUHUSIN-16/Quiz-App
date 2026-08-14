from fastapi import APIRouter, HTTPException
from app.db.mongo import db
from app.schemas.api import ErrorResponse, UserItem, UserListResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserListResponse)
def list_users():
    items = list(db.users.find({}).limit(100))
    for it in items:
        it["id"] = it.pop("_id")
    return {"users": items}


@router.get("/{user_id}", response_model=UserItem, responses={404: {"model": ErrorResponse}})
def get_user(user_id: str):
    u = db.users.find_one({"_id": user_id})
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u["id"] = u.pop("_id")
    return u
