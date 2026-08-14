from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pathlib

# Load .env from backend/ directory (works when running scripts from repo root)
here = pathlib.Path(__file__).resolve()
backend_env = here.parents[2] / ".env"
if backend_env.exists():
	load_dotenv(backend_env)
else:
	# fallback to default behavior (load from current working directory)
	load_dotenv()

# Read connection string from environment (recommended) or fall back to localhost for dev
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
	print("Warning: MONGO_URL not set. Defaulting to localhost. Set MONGO_URL to your MongoDB Atlas SRV string in environment or backend/.env")
	MONGO_URL = "mongodb://localhost:27017"

# Optional DB name
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "quiz_app")

client = MongoClient(MONGO_URL)
db = client.get_database(MONGO_DBNAME)
