"""
Configuration Module for Previous Year Question Paper Analyzer (PYQ Analyzer).
Centralizes path settings, AI/LLM configurations, scoring parameters, and taxonomy defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"
ASSETS_DIR = BASE_DIR / "assets"
SAMPLES_DIR = BASE_DIR / "sample_data"

# Ensure runtime directories exist
for directory in [DB_DIR, UPLOADS_DIR, EXPORTS_DIR, ASSETS_DIR, SAMPLES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = os.getenv("DATABASE_PATH", str(DB_DIR / "pyq_analyzer.db"))

# Application Branding & Metadata
APP_NAME = "PYQ Analyzer"
APP_FULL_NAME = "Previous Year Question Paper Analyzer"
APP_VERSION = "1.0.0"
APP_ICON = "📚"

# File Processing Constraints
SUPPORTED_FORMATS = [".pdf", ".docx", ".txt"]
MAX_FILE_SIZE_MB = 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported/Default Subjects
DEFAULT_SUBJECTS = [
    "Database Management Systems (DBMS)",
    "Operating Systems",
    "Computer Networks",
    "Data Structures & Algorithms",
    "Software Engineering",
    "Computer Architecture",
    "Theory of Computation",
    "Machine Learning & AI",
    "Mathematics for Computing",
    "Other / Custom Subject"
]

# AI / LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
AVAILABLE_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-3.5-turbo"
]
LLM_TEMPERATURE = 0.1
LLM_BATCH_SIZE = 5
MAX_TOKENS = 2500

# Priority Scoring Formula Parameters
# Priority Score = (Topic Frequency / Max Frequency * FREQUENCY_WEIGHT) + (Years Appeared / Total Years * YEARS_WEIGHT)
FREQUENCY_WEIGHT = 60.0
YEARS_WEIGHT = 40.0

# Priority Category Thresholds
PRIORITY_VERY_HIGH = 75.0
PRIORITY_HIGH = 50.0
PRIORITY_MEDIUM = 25.0

# Educational Taxonomy & Categorization Constants
BLOOM_LEVELS = [
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create"
]

QUESTION_TYPES = [
    "Theory",
    "Numerical",
    "Code/Design",
    "Derivation",
    "Case Study",
    "Multiple Choice"
]

DIFFICULTY_LEVELS = [
    "Easy",
    "Medium",
    "Hard"
]
