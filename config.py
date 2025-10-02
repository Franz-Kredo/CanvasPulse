# config.py
"""
Configuration for the Canvas assignment fetcher.
Loads environment variables and sets static parameters.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- Environment Loading ---
# Load .env file from the script's directory
script_dir = Path(__file__).resolve().parent
load_dotenv(script_dir / ".env")

# --- Canvas API Configuration ---
CANVAS_BASE_URL = "https://reykjavik.instructure.com/"
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")

if not CANVAS_TOKEN:
    sys.exit("Error: Missing CANVAS_TOKEN in .env file.")

# --- API Request Parameters ---
COURSE_PARAMS = {
    "enrollment_state": "active",
    "state[]": "available",
    "per_page": 100,
    "include[]": ["term"],
}

ASSIGNMENT_PARAMS = {
    "per_page": 100,
    "include[]": ["submission", "assignment_visibility"],
}

# --- Filtering Rules ---
# List of course IDs to include in the report
COURSE_IDS = [9424, 9425, 9411, 9419]

# List of assignment IDs to always exclude
AVOID_ASSIGNMENT_IDS = [98301, 96732, 98019]

# Window in days to show an unsubmitted assignment after its due date
OVERDUE_WINDOW_DAYS = 7

# --- Display/Formatting ---
# ANSI color codes for console output
class Colors:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    GREY = "\033[90m"
    BLUE = "\033[94m"
    ORANGE = "\033[38;5;208m"
    RESET = "\033[0m"