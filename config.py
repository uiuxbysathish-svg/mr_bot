import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# Configuration variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8821598678:AAFVrO1vMFrokqGe0vUOZaLNiu75XQ5tFyw")
DATABASE_SUBPATH = os.getenv("DATABASE_PATH", "database/mr_database.db")

# Dynamic DB path resolving to ensure database is created in the right sub-folder
DATABASE_PATH = BASE_DIR / DATABASE_SUBPATH

# Ensure database directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
