"""Create recommended indexes for analytics.
Run: python backend/scripts/create_indexes.py
"""
import os
from dotenv import load_dotenv
import pathlib
from pymongo import MongoClient

# load backend/.env
here = pathlib.Path(__file__).resolve()
backend_env = here.parents[1] / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
else:
    load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "quiz_app")
client = MongoClient(MONGO_URL)
db = client.get_database(MONGO_DBNAME)

def main():
    print("Creating indexes on attempts collection...")
    col = db.attempts
    print("Creating event-query indexes")
    col.create_index([("user_id", 1), ("submitted_at", -1)], name="user_submitted")
    col.create_index([("question_id", 1)], name="question")
    col.create_index([("quiz_id", 1), ("question_number", 1)], name="quiz_sequence")
    col.create_index([("chapter_id", 1), ("question_id", 1)], name="chapter_question")
    db.questions.create_index([("chapter_id", 1)], name="question_chapter")
    db.subjects.create_index([("exam_id", 1)], name="subject_exam")
    db.chapters.create_index([("subject_id", 1)], name="chapter_subject")
    print("Indexes created.")

if __name__ == '__main__':
    main()
