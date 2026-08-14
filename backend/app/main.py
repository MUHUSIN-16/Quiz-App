import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routers import analytics, chapters, exams, quiz, subjects, submit, users

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


app.include_router(exams.router)
app.include_router(subjects.router)
app.include_router(chapters.router)
app.include_router(quiz.router)
app.include_router(submit.router)
app.include_router(analytics.router)
app.include_router(users.router)


# In the Docker deployment, FastAPI serves the compiled React application from
# the same origin as the API. Local development continues to use Vite instead.
frontend_dist = Path(os.getenv("FRONTEND_DIST", Path(__file__).resolve().parents[2] / "frontend" / "dist"))
if frontend_dist.is_dir():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        return FileResponse(frontend_dist / "index.html")
