import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./candidate_review.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "backend/uploads")
MODEL_NAME = os.getenv("MODEL_NAME", "claude-sonnet-4-6")

os.makedirs(UPLOAD_DIR, exist_ok=True)
