"""Central configuration, read from environment variables (.env supported)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
DB_PATH = os.getenv("DB_PATH", "conversations.db")
DB_CONNECTION_STRING = f"sqlite:///{DB_PATH}"
PROMPT_PATH = Path(__file__).with_name("prompt.md")
