"""
Seed script to populate MongoDB with dummy data:
- Users
- Exams
- Subjects
- Chapters
- Questions

Run: python backend/scripts/seed_db.py
"""
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pathlib

fake = Faker()

CURRICULUM = [
    ("Modern Web Development", [
        ("HTML & CSS", ["Semantic HTML", "CSS layout", "Responsive design"]),
        ("JavaScript", ["Variables and scope", "Asynchronous JavaScript", "The DOM"]),
        ("React", ["Components and props", "State and hooks", "Routing"]),
        ("Web Performance", ["Browser rendering", "Caching", "Core Web Vitals"]),
    ]),
    ("Backend & APIs", [
        ("Python Fundamentals", ["Data structures", "Functions", "Error handling"]),
        ("Databases", ["Relational modeling", "SQL queries", "Indexes and transactions"]),
        ("API Design", ["HTTP methods", "REST conventions", "Authentication"]),
    ]),
    ("Cloud, Data & Security", [
        ("Cloud Computing", ["Compute and storage", "Containers", "Serverless"]),
        ("Data Engineering", ["Data pipelines", "Data warehouses", "Data quality"]),
        ("Cybersecurity", ["Web security", "Identity and access", "Network security"]),
    ]),
]

QUESTION_BANK = [
    ("Which HTML element represents the main navigation links on a page?", ["<nav>", "<aside>", "<footer>", "<article>"], 0),
    ("Which CSS layout system is designed for one-dimensional rows or columns?", ["Flexbox", "CSS Grid", "Float", "Table layout"], 0),
    ("What does the CSS property box-sizing: border-box change?", ["Width includes padding and border", "It removes margins", "It centers an element", "It enables grid"], 0),
    ("What does JavaScript's const keyword prevent?", ["Reassigning the binding", "Changing an object property", "Calling a function", "Reading a variable"], 0),
    ("Which JavaScript feature is commonly used to wait for a Promise?", ["await", "yield", "break", "throw"], 0),
    ("What is the purpose of addEventListener?", ["Attach a handler to an event", "Create a database record", "Import a module", "Style an element"], 0),
    ("What is a React component?", ["A reusable piece of UI", "A database table", "A browser extension", "A CSS property"], 0),
    ("Which React hook stores local component state?", ["useState", "useEffect", "useMemo", "useRef"], 0),
    ("Why should a list rendered in React have a key?", ["To identify items between renders", "To encrypt data", "To add CSS", "To create a route"], 0),
    ("What does an HTTP 404 status code mean?", ["The requested resource was not found", "The request succeeded", "Authentication is required", "The server crashed"], 0),
    ("Which HTTP method is conventionally used to create a resource?", ["POST", "GET", "DELETE", "HEAD"], 0),
    ("What is a primary purpose of a database index?", ["Speed up data retrieval", "Encrypt every row", "Replace backups", "Validate HTML"], 0),
    ("What does ACID consistency help preserve in a database?", ["Valid data rules across transactions", "CSS styles", "API route names", "Image resolution"], 0),
    ("What is a REST API resource commonly identified by?", ["A URL", "A CSS selector", "A package name", "A browser tab"], 0),
    ("What is the safest way to store a user password?", ["A slow salted hash", "Plain text", "Base64 encoding", "A browser cookie only"], 0),
    ("What does HTTPS add to HTTP?", ["Encrypted transport using TLS", "Faster database queries", "Automatic backups", "A user interface"], 0),
    ("What is a container image?", ["A packaged application and its dependencies", "A physical server", "A database index", "A network cable"], 0),
    ("What does serverless computing generally manage for you?", ["Server provisioning and scaling", "Your source code", "Your users", "Your passwords"], 0),
    ("What does a data pipeline do?", ["Moves and transforms data between systems", "Renders a web page", "Encrypts a CSS file", "Creates a password"], 0),
    ("What is the principle of least privilege?", ["Grant only the access needed", "Give every user admin rights", "Never use passwords", "Avoid logging"], 0),
]

# Ensure backend/.env is loaded when running from repo root
here = pathlib.Path(__file__).resolve()
backend_env = here.parents[1] / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
else:
    load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client.get_database(os.getenv("MONGO_DBNAME", "quiz_app"))


def clear_collections():
    for name in ["users", "exams", "subjects", "chapters", "questions", "quizzes", "attempts"]:
        if name in db.list_collection_names():
            db[name].drop()


def create_users(n=50):
    users = []
    for i in range(n):
        users.append({
            "_id": str(uuid.uuid4()),
            "name": fake.name(),
            "email": fake.unique.email(),
        })
    db.users.insert_many(users)
    return users


def create_exams_subjects_chapters():
    exams = []
    subjects = []
    chapters = []

    for exam_title, subject_specs in CURRICULUM:
        exam_id = str(uuid.uuid4())
        exams.append({"_id": exam_id, "title": exam_title})
        for subject_title, chapter_titles in subject_specs:
            subject_id = str(uuid.uuid4())
            subjects.append({"_id": subject_id, "exam_id": exam_id, "title": subject_title})
            for chapter_title in chapter_titles:
                chapters.append({"_id": str(uuid.uuid4()), "subject_id": subject_id, "title": chapter_title})

    db.exams.insert_many(exams)
    db.subjects.insert_many(subjects)
    db.chapters.insert_many(chapters)
    return exams, subjects, chapters


def create_questions(chapters, n=500):
    """Create unique prompts per chapter, avoiding repeated quiz questions."""
    questions = []
    base_count, remainder = divmod(n, len(chapters))
    for chapter_index, chapter in enumerate(chapters):
        chapter_count = base_count + (1 if chapter_index < remainder else 0)
        start = (chapter_index * 7) % len(QUESTION_BANK)
        for question_index in range(chapter_count):
            text, base_options, correct_idx = QUESTION_BANK[(start + question_index) % len(QUESTION_BANK)]
            # A second pass uses a distinct practical framing rather than copying text.
            if question_index >= len(QUESTION_BANK):
                text = f"During a review of {chapter['title'].lower()}, {text[0].lower() + text[1:]}"
            options = list(base_options)
            shift = (chapter_index + question_index) % len(options)
            options = options[shift:] + options[:shift]
            questions.append({
                "_id": str(uuid.uuid4()),
                "chapter_id": chapter["_id"],
                "text": text,
                "options": options,
                "correct_option": (correct_idx - shift) % len(options),
            })
    db.questions.insert_many(questions)
    return questions


def create_attempts(users, exams, subjects, chapters, questions, approx_events=5000):
    # Preload chapter -> subject -> exam mappings to avoid DB reads per attempt
    chapter_map = {c["_id"]: c for c in db.chapters.find({})}
    subject_map = {s["_id"]: s for s in db.subjects.find({})}
    exam_map = {e["_id"]: e for e in db.exams.find({})}

    attempts = []
    quizzes = []
    chunk = 1000
    event_count = 0
    # Events are generated as real quiz sessions, enabling meaningful fatigue analysis.
    while event_count < approx_events:
        user = random.choice(users)
        session_questions = random.sample(questions, min(10, len(questions), approx_events - event_count))
        quiz_id = str(uuid.uuid4())
        start = datetime.utcnow() - timedelta(seconds=random.randint(0, 60 * 60 * 24 * 30))
        quizzes.append({"_id": quiz_id, "user_id": user["_id"], "question_ids": [q["_id"] for q in session_questions],
                       "current_index": len(session_questions), "status": "completed", "started_at": start, "completed_at": start})
        for position, question in enumerate(session_questions, 1):
            chapter_id = question["chapter_id"]
            subject = subject_map.get(chapter_map.get(chapter_id, {}).get("subject_id"), {})
            exam = exam_map.get(subject.get("exam_id"), {})
            shown_at = start + timedelta(seconds=(position - 1) * 30)
            duration_ms = random.randint(3000, 45000)
            selected = random.randrange(len(question["options"]))
            attempts.append({"_id": str(uuid.uuid4()), "user_id": user["_id"], "quiz_id": quiz_id,
                "question_id": question["_id"], "exam_id": exam.get("_id"), "subject_id": subject.get("_id"),
                "chapter_id": chapter_id, "question_number": position, "shown_at": shown_at,
                "submitted_at": shown_at + timedelta(milliseconds=duration_ms), "duration_ms": duration_ms,
                "selected_option": selected, "correct": selected == question["correct_option"]})
            event_count += 1

        # Insert in chunks to keep memory usage bounded and show progress
        if len(attempts) >= chunk:
            db.attempts.insert_many(attempts)
            db.quizzes.insert_many(quizzes)
            print(f"Inserted {event_count} / {approx_events} attempts")
            attempts = []
            quizzes = []

    # final flush
    if attempts:
        db.attempts.insert_many(attempts)
        db.quizzes.insert_many(quizzes)

    return approx_events


def main():
    print("Clearing existing collections (if any)...")
    clear_collections()
    print("Creating users...")
    users = create_users(50)
    print("Creating exams, subjects, chapters...")
    exams, subjects, chapters = create_exams_subjects_chapters()
    print("Creating questions...")
    questions = create_questions(chapters, 500)
    print("Creating attempts/events...")
    count = create_attempts(users, exams, subjects, chapters, questions, approx_events=5000)
    print(f"Seed complete: users={len(users)}, exams={len(exams)}, subjects={len(subjects)}, chapters={len(chapters)}, questions={len(questions)}, attempts={count}")


if __name__ == "__main__":
    main()
