from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import exams

app = FastAPI(title="Quiz Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# include routers
app.include_router(exams.router)


from app.api.routers import subjects, chapters, quiz, submit, analytics, users, admin

app.include_router(subjects.router)
app.include_router(chapters.router)
app.include_router(quiz.router)
app.include_router(submit.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(admin.router)
