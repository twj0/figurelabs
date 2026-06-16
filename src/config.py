"""App-wide settings loaded from environment / .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PORT: int = int(os.getenv("PORT", "11451"))
DB_PATH: str = os.getenv("DB_PATH", "./data/figurelabs.db")

# Ensure parent directory exists at import time
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
