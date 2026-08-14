import os
from dotenv import load_dotenv
import pathlib
from pymongo import MongoClient

# Load backend/.env relative to this file
here = pathlib.Path(__file__).resolve()
backend_env = here.parents[1] / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
else:
    load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')

def redact(url: str) -> str:
    if not url:
        return None
    try:
        # hide password between : and @ for basic SRV or normal URLs
        import re
        return re.sub(r':[^@]+@', ':***@', url)
    except Exception:
        return url

print('Using MONGO_URL (redacted):', redact(MONGO_URL))

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    info = client.server_info()
    print('Connected to MongoDB. Server info keys:', list(info.keys())[:5])
    print('Databases:', client.list_database_names()[:10])
except Exception as e:
    print('Connection failed:')
    import traceback
    traceback.print_exc()
    print(repr(e))
