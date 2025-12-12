"""Configuration and constants for Smart CV application."""
import os

# Database
DB_PATH = "data/app.db"

# Logging
LOG_DIR = "logs"
LOG_FILE = "logs/app.log"

# API Keys
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY")
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")

# LLM Model
LLM_MODEL_NAME = "gemini-2.5-flash"
