---
title: QuizFlow
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# QuizFlow

QuizFlow is a full-stack quiz application built with React, FastAPI, and MongoDB. It guides a learner through a one-way quiz flow:

**Login → Exam → Subject → Chapter → Quiz → Result**

Questions are served one at a time. Once an answer is submitted, the learner cannot return to that question. The app records attempt events for learning-velocity, fatigue, and question-difficulty analytics.

## Tech stack

- **Frontend:** React 18, Vite, React Router, Axios
- **Backend:** FastAPI, Uvicorn, Pydantic
- **Database:** MongoDB with PyMongo
- **Testing:** Pytest and HTTPX

## Prerequisites

Install the following before starting:

- [Node.js](https://nodejs.org/) 18 or later (includes npm)
- Python 3.10 or later
- One of the following MongoDB options:
  - MongoDB Community Server running locally, or
  - a MongoDB Atlas database connection string

## Project structure

```text
Quiz-App/
├── backend/       # FastAPI API, database scripts, and Python dependencies
├── frontend/      # React + Vite application
├── docs/          # Architecture and database documentation
├── infra/         # Infrastructure-related files
└── tests/         # Backend tests
```

## Run locally

Open PowerShell in the project root and complete the steps below.

### 1. Configure MongoDB

Create a local environment file from the example:

```powershell
Copy-Item backend/.env.example backend/.env
```

Edit `backend/.env` and choose one configuration.

For local MongoDB:

```env
MONGO_URL=mongodb://localhost:27017
MONGO_DBNAME=quiz_app
```

For MongoDB Atlas, paste your connection string in `MONGO_URL`. Replace `<PASSWORD>` in the example file with your Atlas database-user password.

### 2. Set up and install the backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, run this once for the current terminal and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. Verify the database and seed sample data

Still inside `backend`, optionally verify the MongoDB connection first:

```powershell
python scripts/test_conn.py
```

Then create indexes and sample data:

```powershell
python scripts/create_indexes.py
python scripts/seed_db.py
```

The seed script creates users, exams, subjects, chapters, questions, and quiz-attempt data for the analytics pages.

### 4. Start the backend API

Keep the virtual environment active and run:

```powershell
uvicorn app.main:app --reload
```

The API starts at [http://localhost:8000](http://localhost:8000). Confirm it is running at [http://localhost:8000/health](http://localhost:8000/health), then view interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Start the frontend

Open a **second** PowerShell terminal in the project root:

```powershell
cd frontend
npm install
npm run start
```

Vite will print the frontend URL in the terminal, usually [http://localhost:5173](http://localhost:5173).

The frontend uses `http://localhost:8000` by default. To use a different API address, create `frontend/.env` with:

```env
VITE_API_URL=http://localhost:8000
```

Restart the Vite server after changing this value.

## Available commands

| Location | Command | Purpose |
| --- | --- | --- |
| `backend` | `python scripts/test_conn.py` | Check MongoDB connectivity. |
| `backend` | `python scripts/create_indexes.py` | Create database indexes. |
| `backend` | `python scripts/seed_db.py` | Populate sample data. |
| `backend` | `uvicorn app.main:app --reload` | Start the API in development mode. |
| `frontend` | `npm run start` | Start the Vite development server. |
| `frontend` | `npm run build` | Create a production frontend build. |

## Analytics endpoints

| Endpoint | Description |
| --- | --- |
| `GET /analytics/learning-velocity` | Ranks users using accuracy (60%), speed (25%), and consistency (15%). |
| `GET /analytics/fatigue?quiz_id=...&window=5` | Shows accuracy and response time across consecutive question windows. |
| `GET /analytics/question-difficulty` | Ranks questions by error rate (70%) and normalized response time (30%). |

## Deploy to Hugging Face Spaces

This repository is ready for deployment as a **Docker Space**. The Docker image builds the React frontend and serves it from the same FastAPI application, so the deployed site and API share one URL.

1. Create a new Space at [Hugging Face Spaces](https://huggingface.co/new-space) with **Docker** as the SDK and **Public** visibility.
2. In the new Space, open **Settings → Variables and secrets** and add a secret named `MONGO_URL` containing your MongoDB Atlas connection string. Add a variable named `MONGO_DBNAME` with the value `quiz_app`.
3. Copy the Space Git URL from its page, then push this repository to it:

   ```powershell
   git remote add huggingface https://huggingface.co/spaces/<your-username>/quizflow.git
   git push huggingface main
   ```

4. Wait for the Docker build to finish, then open the Space URL. Verify `/health`, `/docs`, and the quiz flow.

Do not commit `backend/.env` or your Atlas password. Hugging Face injects Space secrets as runtime environment variables for Docker apps.

## Troubleshooting

- **`MONGO_URL not set` or database connection fails:** confirm `backend/.env` exists, its connection string is valid, and MongoDB is running or Atlas access is allowed.
- **Frontend cannot reach the API:** start the backend first and verify `http://localhost:8000/health`. If the backend uses another address, update `VITE_API_URL` in `frontend/.env`.
- **`npm` or `python` is not recognized:** install the corresponding prerequisite and reopen PowerShell.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Database schema](docs/DB_SCHEMA.md)
